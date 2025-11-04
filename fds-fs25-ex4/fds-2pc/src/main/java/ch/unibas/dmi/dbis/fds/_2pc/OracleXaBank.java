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
    @Override
    public void transfer(final AbstractOracleXaBank TO_BANK, final String ibanFrom, final String ibanTo, final float value) {

        // Prepare resources
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
            gtrid  = this.getXid();                 // global id
            fromXid = this.getXid(gtrid);           // branch 1 (debit)
            toXid   = TO_BANK.getXid(gtrid);        // branch 2 (credit)

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

            // PREPARE both
            int p1 = fromRes.prepare(fromXid);
            int p2 = toRes.prepare(toXid);

            // If both prepared OK or read-only, COMMIT both (two-phase)
            if ((p1 == XAResource.XA_OK || p1 == XAResource.XA_RDONLY) &&
                (p2 == XAResource.XA_OK || p2 == XAResource.XA_RDONLY)) {

                // XA_RDONLY means nothing to commit for that branch
                if (p1 != XAResource.XA_RDONLY) fromRes.commit(fromXid, false);
                if (p2 != XAResource.XA_RDONLY) toRes.commit(toXid, false);
            } else {
                // anything else: roll back both
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
            // close JDBC resources (do NOT commit/rollback here; XA handles that)
            try { if (debitStmt  != null) debitStmt.close(); }  catch (Exception ignore) {}
            try { if (creditStmt != null) creditStmt.close(); } catch (Exception ignore) {}
            try { if (fromConn   != null) fromConn.close(); }   catch (Exception ignore) {}
            try { if (toConn     != null) toConn.close(); }     catch (Exception ignore) {}
        }
    }

}