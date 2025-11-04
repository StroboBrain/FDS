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


     // Implementation of Exercise
    @Override
    public float getBalance(final String iban) throws SQLException {

        // Existence check before querying balance (Could be refactored into a separate method)
        try (PreparedStatement checkStmt = this.getXaConnection().getConnection()
                .prepareStatement("SELECT 1 FROM account WHERE iban = ?")) {
            checkStmt.setString(1, iban);
            try (ResultSet rs = checkStmt.executeQuery()) {
                if (!rs.next()) {
                    throw new SQLException("Account with IBAN " + iban + " not found.");
                }
            }
        }

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
        }
    }

    // Implementation of Exercise
    // Some ugly code duplication, could be refactored
    @Override
    public void transfer(final AbstractOracleXaBank TO_BANK, final String ibanFrom, final String ibanTo, final float value) {
    

        // Validate input
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

        // --- Prepare resources for XA transaction ---
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
            /*Answer Question b) TODO: Review Answer
            IN this code-block Presumed Abort 2pc would be implemented if possible, this would have the advantage to automatically roll back on failure. We rely on manual rollback
            We don't see an advantage to implement Transfer of Coordination, because we rely on exceptions to trigger rollbacks. */

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
    }


}