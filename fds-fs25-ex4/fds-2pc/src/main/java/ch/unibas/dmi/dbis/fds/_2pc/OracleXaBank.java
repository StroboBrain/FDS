package ch.unibas.dmi.dbis.fds._2pc;


import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import javax.sql.XAConnection;
import javax.transaction.xa.XAResource;
import javax.transaction.xa.Xid;


/**
 * Check the XA stuff here --> https://docs.oracle.com/cd/B14117_01/java.101/b10979/xadistra.htm
 *
 * @author Alexander Stiemer (alexander.stiemer at unibas.ch)
 */
public class OracleXaBank extends AbstractOracleXaBank {


    public OracleXaBank( final String BIC, final String jdbcConnectionString, final String dbmsUsername, final String dbmsPassword ) throws SQLException {
        super( BIC, jdbcConnectionString, dbmsUsername, dbmsPassword );
    }


    //NM: We only read here so we don't need a 2PC.
    //NM: prepare a connection and get the value. It closes automatically.
     // Implementation of Exercise
    @Override
    public float getBalance(final String iban) throws SQLException {

        // Existence check before querying balance (Could be refactored into a separate method)
        final String sql = "SELECT Balance FROM account WHERE IBAN = ?";
        try (Connection c = getXaConnection().getConnection();
            PreparedStatement ps = c.prepareStatement(sql)) {
            ps.setString(1, iban);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) {
                    throw new SQLException("Account with IBAN " + iban + " not found.");
                }
                return rs.getFloat("balance");
            }
        }
    }
        /*
        // Set up resources
        XAConnection xaConnection = null;
        PreparedStatement statement = null;
        ResultSet resultSet = null;

        try {
            xaConnection = getXaConnection();
            
            // Prepare and execute SQL query
            String sql = "SELECT balance FROM account WHERE iban = ?";
            statement = xaConnection.getConnection().prepareStatement(sql);
            statement.setString(1, iban);
            resultSet = statement.executeQuery();

            if (resultSet.next()) {
                return resultSet.getFloat("balance");
            } else {
                // If IBAN not found, throw an exception
                throw new SQLException("Account with IBAN " + iban + " not found.");
            }

        } finally {
            // Close resources safely except xaConnection
            if (resultSet != null) {
                resultSet.close();
            }
            if (statement != null) {
                statement.close();
            }
        }*/

    // Implementation of Exercise
    // Some ugly code duplication, could be refactored
    @Override
    public void transfer(final AbstractOracleXaBank TO_BANK, final String ibanFrom, final String ibanTo, final float value) {
    
        Xid xidA = null;
        Xid xidB = null;
        boolean failed = false;
        try {
            //NM: Here we start setup a new global transaction id (gtrid) with 2 branches. Both have the same gtrid but are seperate branches.
            xidA = this.startTransaction();
            xidB = TO_BANK.startTransaction(xidA);
            
            try(Connection cA = this.getXaConnection().getConnection();
                Connection cB = TO_BANK.getXaConnection().getConnection();
                ){
                
                withdraw(cA, ibanFrom, value);
                deposit(cB, ibanTo, value);

            }
            this.endTransaction(xidA, false);
            TO_BANK.endTransaction(xidB, false); //NM: should give us TMSUCCESS-Flag

            //(From prepare Method): Returns A value indicating the resource manager's vote on the outcome of the transaction. 
            //The possible values are: XA_RDONLY or XA_OK. If the resource manager wants to roll back the transaction, it should do so by raising an appropriate XAException in the prepare method.
            int pA = this.getXaResource().prepare(xidA);
            int pB = TO_BANK.getXaResource().prepare(xidB);
            /*Answer Question b) TODO: Review Answer
            IN this code-block Presumed Abort 2pc would be implemented if possible, this would have the advantage to automatically roll back on failure. We rely on manual rollback
            We don't see an advantage to implement Transfer of Coordination, because we rely on exceptions to trigger rollbacks. */
            if (pA == XAResource.XA_OK && pB == XAResource.XA_OK) {
                this.getXaResource().commit(xidA, false);
                TO_BANK.getXaResource().commit(xidB, false);
            }else{
                failed = true;
                safeRollbackBoth(this, xidA, TO_BANK, xidB);
            }
        }catch(Exception e){
            failed = true;
            try {
                if (xidA != null) {
                    this.endTransaction(xidA, failed);
                }
            } catch (Exception ignore) {}
            try {
                if (xidB != null) {
                    TO_BANK.endTransaction(xidB, failed);
                }
            } catch (Exception ignore) {}

            throw new RuntimeException("Transfeir failed: "+ e.getMessage(), e);
        }
    }
        /*// Validate input
        if (value <= 0) {
            throw new IllegalArgumentException("We are a bank, transfer value must be positive.");
        }
        // No transfers to self
        if (ibanFrom.equals(ibanTo)) {
            System.out.println("Transfer within the same account is weird, but allowed");
        }

        // Existence checks for both IBAN
        try (PreparedStatement stmt = this.getXaConnection().getConnection()
                .prepareStatement("SELECT 1 FROM account WHERE iban = ?")) {
            stmt.setString(1, ibanFrom);
            try (ResultSet rs = stmt.executeQuery()) {
                if (!rs.next()) {
                    throw new SQLException("Source account with IBAN " + ibanFrom + " not found.");
                }
            }
        } catch (SQLException e) {
            throw new RuntimeException("Failed to validate source account: " + e.getMessage(), e);
        }

        try (PreparedStatement stmt = TO_BANK.getXaConnection().getConnection()
                .prepareStatement("SELECT 1 FROM account WHERE iban = ?")) {
            stmt.setString(1, ibanTo);
            try (ResultSet rs = stmt.executeQuery()) {
                if (!rs.next()) {
                    throw new SQLException("Destination account with IBAN " + ibanTo + " not found.");
                }
            }
        } catch (SQLException e) {
            throw new RuntimeException("Failed to validate destination account: " + e.getMessage(), e);
        }
        
        //  Prepare resources for XA transaction 
        Xid gtrid = null;
        Xid fromXid = null;
        Xid toXid   = null;

        XAResource fromRes = this.getXaResource();
        XAResource toRes   = TO_BANK.getXaResource();

        Connection fromConn = null;
        Connection toConn   = null;

        PreparedStatement debitStmt  = null;
        PreparedStatement creditStmt = null;

        try {
            gtrid  = this.getXid();
            fromXid = this.getXid(gtrid);
            toXid   = TO_BANK.getXid(gtrid);

            // start FROM branch
            fromRes.start(fromXid, XAResource.TMNOFLAGS);
            fromConn = this.getXaConnection().getConnection();
            debitStmt = fromConn.prepareStatement(
                    "UPDATE account SET balance = balance - ? WHERE iban = ?");
            debitStmt.setFloat(1, value);
            debitStmt.setString(2, ibanFrom);
            debitStmt.executeUpdate();
            fromRes.end(fromXid, XAResource.TMSUCCESS);

            // start TO branch
            toRes.start(toXid, XAResource.TMNOFLAGS);
            toConn = TO_BANK.getXaConnection().getConnection();
            creditStmt = toConn.prepareStatement(
                    "UPDATE account SET balance = balance + ? WHERE iban = ?");
            creditStmt.setFloat(1, value);
            creditStmt.setString(2, ibanTo);
            creditStmt.executeUpdate();
            
            toRes.end(toXid, XAResource.TMSUCCESS);

            // PREPARE both banks
            int p1 = fromRes.prepare(fromXid);
            int p2 = toRes.prepare(toXid);

            // If both prepared OK or read-only, we COMMIT

            if ((p1 == XAResource.XA_OK || p1 == XAResource.XA_RDONLY) &&
                (p2 == XAResource.XA_OK || p2 == XAResource.XA_RDONLY)) {

                // XA_RDONLY means nothing to commit for that branch
                if (p1 != XAResource.XA_RDONLY) fromRes.commit(fromXid, false);
                if (p2 != XAResource.XA_RDONLY) toRes.commit(toXid, false);
            } else {
                // anything else: roll back both, ignore rollback errors
                try { fromRes.rollback(fromXid); } catch (Exception ignore) {}
                try { toRes.rollback(toXid); }   catch (Exception ignore) {}
                throw new RuntimeException("Prepare failed on at least one branch.");
            }

        } catch (Exception e) {
            // best-effort global rollback if we have branch ids
            try { if (fromXid != null) fromRes.end(fromXid, XAResource.TMFAIL); } catch (Exception ignore) {}
            try { if (toXid   != null) toRes.end(toXid,   XAResource.TMFAIL); }   catch (Exception ignore) {}
            try { if (fromXid != null) fromRes.rollback(fromXid); } catch (Exception ignore) {}
            try { if (toXid   != null) toRes.rollback(toXid); }     catch (Exception ignore) {}
            throw new RuntimeException("XA transfer failed", e);
        } finally {
            // close resources
            try { if (debitStmt  != null) debitStmt.close(); }  catch (Exception ignore) {}
            try { if (creditStmt != null) creditStmt.close(); } catch (Exception ignore) {}
            try { if (fromConn   != null) fromConn.close(); }   catch (Exception ignore) {}
            try { if (toConn     != null) toConn.close(); }     catch (Exception ignore) {}
        }
    }*/

     private static void withdraw(Connection c, String ibanFrom, float value) throws SQLException {
        float balance = selectBalanceForUpdate(c, ibanFrom);
        //check if we want to withdraw more than we have.
        if (balance < value) {
            throw new SQLException("Insufficient funds on " + ibanFrom + " (" + balance + " < " + value + ")");
        }
        try (PreparedStatement up = c.prepareStatement(
                "UPDATE account SET Balance = Balance - ? WHERE IBAN = ?")) {
            up.setFloat(1, value);
            up.setString(2, ibanFrom);
            if (up.executeUpdate() != 1) {
                throw new SQLException("Withdraw update failed for " + ibanFrom);
            }
        }
    }

    private static void deposit(Connection c, String ibanTo, float value) throws SQLException {
        float balance = selectBalanceForUpdate(c, ibanTo);
        //NM: We might need to check here because we have a constraint in abstractOracleXABank, that max is 15000.
        if (balance + value > 15000.0f) {
            throw new SQLException("Capacity exceeded on " + ibanTo + " (" + balance + " + " + value + " > 15000)");
        }
        try (PreparedStatement up = c.prepareStatement(
                "UPDATE account SET Balance = Balance + ? WHERE IBAN = ?")) {
            up.setFloat(1, value);
            up.setString(2, ibanTo);
            if (up.executeUpdate() != 1) {
                throw new SQLException("Deposit update failed for " + ibanTo);
            }
        }
    }

    private static float selectBalanceForUpdate(Connection c, String iban) throws SQLException {
        //NM: locks the row until the Branch ends to prevent lost updates if the row disapears?
        try (PreparedStatement ps = c.prepareStatement(
                "SELECT Balance FROM account WHERE IBAN = ? FOR UPDATE")) {
            ps.setString(1, iban);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) {
                    throw new SQLException("IBAN not found: " + iban);
                }
                return rs.getFloat(1);
            }
        }
    }

    private static void safeRollbackBoth(OracleXaBank a, Xid xidA, AbstractOracleXaBank bBank, Xid xidB) {
        try { a.getXaResource().rollback(xidA); } catch (Exception ignore) {}
        try { bBank.getXaResource().rollback(xidB); } catch (Exception ignore) {}
    }

}