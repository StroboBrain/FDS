package ch.unibas.dmi.dbis.fds.p2p.chord.impl;

//used import so that ChordNodes are supported?

//import sun.tools.jstat.Identifier; dafuq is this?
import ch.unibas.dmi.dbis.fds.p2p.chord.api.*;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.ChordNetwork;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.data.Identifier;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.data.IdentifierCircularInterval;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.math.CircularInterval;

import java.util.Optional;
import java.util.Random;
import java.util.Set;

import static ch.unibas.dmi.dbis.fds.p2p.chord.api.data.IdentifierCircularInterval.createOpen;

/**
 * TODO: write JavaDoc
 *
 * @author loris.sauter
 */
public class ChordPeer extends AbstractChordPeer {
  /**
   *
   * @param identifier
   * @param network
   */
  protected ChordPeer(Identifier identifier, ChordNetwork network) {
    super(identifier, network);
  }

  /**
   * Asks this {@link ChordNode} to find {@code id}'s successor {@link ChordNode}.
   *
   * Defined in [1], Figure 4
   *
   * @param caller The calling {@link ChordNode}. Used for simulation - not part of the actual chord definition.
   * @param id The {@link Identifier} for which to lookup the successor. Does not need to be the ID of an actual {@link ChordNode}!
   * @return The successor of the node {@code id} from this {@link ChordNode}'s point of view
   */
  @Override
  public ChordNode findSuccessor(ChordNode caller, Identifier id) {
    /* TODO(done): Implementation required. */
    ChordNode n = findPredecessor(caller, id);
    return n.successor();
  }

  /**
   * Asks this {@link ChordNode} to find {@code id}'s predecessor {@link ChordNode}
   *
   * Defined in [1], Figure 4
   *
   * @param caller The calling {@link ChordNode}. Used for simulation - not part of the actual chord definition.
   * @param id The {@link Identifier} for which to look up the predecessor. Does not need to be the ID of an actual {@link ChordNode}!
   * @return The predecessor of or the node {@code of} from this {@link ChordNode}'s point of view
   */
  @Override
  public ChordNode findPredecessor(ChordNode caller, Identifier id) {
    /* TODO(done): Implementation required. */

    ChordNode node = this.predecessor();
    ChordNode succ;
    int node_id;
    int succ_id;
    int ident_id;
    int m = this.getNetwork().getNbits();
    do {
      node = node.successor();
      node_id = node.id().getIndex();
      succ = node.successor();
      succ_id = succ.id().getIndex();
      ident_id = id.getIndex();
      if (succ_id <= node_id) {
        succ_id = succ_id + (int)Math.pow(2, m);
        if (node.predecessor().getIdentifier().getIndex() > ident_id) {
          ident_id = ident_id + (int) Math.pow(2, m);
        }
      }
    } while (!(ident_id > node_id && ident_id <= succ_id));
    return node;

    /*
    ChordNode n = this;
    while (true) { 
        Identifier nId = n.id();
        Identifier succId= n.successor().id();
        int x= id.getIndex();
        int nIdx= nId.getIndex();
        int succIdx= succId.getIndex();

        boolean inInterval;
        if (nIdx < succIdx) {
            inInterval = (x > nIdx) && (x <= succIdx);
        } else {
            inInterval = (x > nIdx) || (x <= succIdx);
        }

        if (inInterval) {
            return n;
        }

        ChordNode cp = n.closestPrecedingFinger(null, id);
        if (cp == null || cp == n) {
            return n;
        }
        n = cp;
    }
    */
  }

  /**
   * Return the closest finger preceding the  {@code id}
   *
   * Defined in [1], Figure 4
   *
   * @param caller The calling {@link ChordNode}. Used for simulation - not part of the actual chord definition.
   * @param id The {@link Identifier} for which the closest preceding finger is looked up.
   * @return The closest preceding finger of the node {@code of} from this node's point of view
   */
  @Override
  public ChordNode closestPrecedingFinger(ChordNode caller, Identifier id) {
    /* TODO(done): Implementation required. */
    ChordNode node = (caller != null) ? caller : this;
    int node_id = node.id().getIndex();
    int m = this.getNetwork().getNbits();
    int ident_id = node_id > id.getIndex() ? id.getIndex() + (int)Math.pow(2, m) : id.getIndex();
    for (int i = m; i >= 1; i--) {
      ChordNode finger = finger().node(i).orElse(null);
      if (finger != null) {
        int finger_id = finger.id().getIndex();
        if (finger_id > node_id && finger_id <= ident_id) {
          return finger;
        }
      }
    }
    return node;
    /*
    ChordNode base = (caller != null) ? caller : this;
    int m = getNetwork().getNbits();

    for (int i = m; i >= 1; i--) {
        ChordNode f = finger().node(i).orElse(null);
        if (f == null) continue;

        Identifier fId = f.id();
        Identifier baseId = base.id();

        IdentifierCircularInterval interval = createOpen(baseId, id);
        if (interval.contains(fId)) {
            return f;
        }
    }
    return base;
     */
  }


  //todo: from CHATGPT and Noah
  // TODO: move keys in (pred, this] from successor  -- später machen
  private void moveMyKeysFromSuccessor(ChordNode succ) {
    if (succ == null || succ == this) return;

    ChordNode pred = this.predecessor();
    Identifier from = (pred != null) ? pred.id() : this.id();
    Identifier to = this.id();

    // (pred, this]
    IdentifierCircularInterval interval =
            IdentifierCircularInterval.createLeftOpen(from, to);

    for (String key : succ.keys()) {
        int h = getNetwork().getHashFunction().hash(key);
        Identifier id = getNetwork().getIdentifierCircle().getIdentifierAt(h);

        if (interval.contains(id)) {
            // erst Wert holen, dann löschen
            String val = succ.lookup(this, key).orElse(null);
            succ.delete(this, key);
            this.store(this, key, val);
        }
    }
}

  /**
   * Called on this {@link ChordNode} if it wishes to join the {@link ChordNetwork}. {@code nprime} references another {@link ChordNode}
   * that is already member of the {@link ChordNetwork}.
   *
   * Required for static {@link ChordNetwork} mode. Since no stabilization takes place in this mode, the joining node must make all
   * the necessary setup.
   *
   * Defined in [1], Figure 6
   *
   * @param nprime Arbitrary {@link ChordNode} that is part of the {@link ChordNetwork} this {@link ChordNode} wishes to join.
   */
  @Override
  public void joinAndUpdate(ChordNode nprime) {
    if (nprime != null) {
      initFingerTable(nprime);
      updateOthers();
      /* TODO(done): Move keys. */
      ChordNode succ = nprime.findSuccessor(nprime, this.id());
      Set<String> keys = succ.keys();
      for (String key: keys) {
        if (Integer.parseInt(key) <= this.getIdentifier().getIndex()) {
          String value = succ.delete(this, key).orElse(null);
          this.store(this, key, value);
        }
      }
      /*
      ChordNode succ = this.successor();
      moveMyKeysFromSuccessor(succ);
      ChordNode pred = this.predecessor();   
        if (pred != null && succ != null && pred != succ) {
            pred.setPredecessor(succ);   
        }
    */
    } else {
      for (int i = 1; i <= getNetwork().getNbits(); i++) {
        this.fingerTable.setNode(i, this);
      }
      this.setPredecessor(this);
    }
  }

  /**
   * Called on this {@link ChordNode} if it wishes to join the {@link ChordNetwork}. {@code nprime} references
   * another {@link ChordNode} that is already member of the {@link ChordNetwork}.
   *
   * Required for dynamic {@link ChordNetwork} mode. Since in that mode {@link ChordNode}s stabilize the network
   * periodically, this method simply sets its successor and waits for stabilization to do the rest.
   *
   * Defined in [1], Figure 7
   *
   * @param nprime Arbitrary {@link ChordNode} that is part of the {@link ChordNetwork} this {@link ChordNode} wishes to join.
   */
  @Override
  public void joinOnly(ChordNode nprime) {
    setPredecessor(null);
    if (nprime == null) {
      this.fingerTable.setNode(1, this);
    } else {
      this.fingerTable.setNode(1, nprime.findSuccessor(this,this.id()));
    }
  }

  /**
   * Initializes this {@link ChordNode}'s {@link FingerTable} based on information derived from {@code nprime}.
   *
   * Defined in [1], Figure 6
   *
   * @param nprime Arbitrary {@link ChordNode} that is part of the network.
   */
  private void initFingerTable(ChordNode nprime) {
    /* TODO(done): Implementation required. */
    if (nprime != null) {
      int m = this.getNetwork().getNbits();
      ChordNode succ = nprime.findSuccessor(nprime, this.id());
      this.fingerTable.setNode(1, succ);
      this.setPredecessor(succ.predecessor());
      succ.setPredecessor(this);
      for (int i = 1; i < m; i++) {
        // Changed constructor of Identifier to public
        this.fingerTable.setNode(i + 1, this.findSuccessor(this, new Identifier(-1, this.fingerTable.start(i + 1))));
      }
    } else {
      for (int i = 1; i <= getNetwork().getNbits(); i++) {
        this.fingerTable.setNode(i, this);
      }
      this.setPredecessor(this);
    }
    /*
    int m = getNetwork().getNbits();

    IdentifierCircle<Identifier> circle = getNetwork().getIdentifierCircle();

    Identifier start1 = circle.getIdentifierAt(finger().start(1));


    ChordNode succ = nprime.findSuccessor(this, start1);
    this.fingerTable.setNode(1, succ);

    this.setPredecessor(succ.predecessor());
    succ.setPredecessor(this);

    for (int i = 1; i < m; i++) {
      Identifier startNext = circle.getIdentifierAt(finger().start(i + 1));
      Identifier thisId = this.id();
      Identifier prevFingerId = finger().node(i).get().id();

      //[thisId, prevId)
      IdentifierCircularInterval interval =
          IdentifierCircularInterval.createRightOpen(thisId, prevFingerId);

      if (interval.contains(startNext)) {
        this.fingerTable.setNode(i + 1, finger().node(i).get());
      } else {
        ChordNode s = nprime.findSuccessor(this, startNext);
        this.fingerTable.setNode(i + 1, s);
      }
  }
  */
  }

  /**
   * Updates all {@link ChordNode} whose {@link FingerTable} should refer to this {@link ChordNode}.
   *
   * Defined in [1], Figure 6
   */
  private void updateOthers() {
    /* TODO ( done): Implementation required. */
    int m = this.getNetwork().getNbits();
    for (int i = 1; i <= m; i++) {
      int n = this.getIdentifier().getIndex();
      int ident_id = n - (int)Math.pow(2, i - 1);
      if (ident_id >= 0 && ident_id <= (int)Math.pow(2, m) - 1) {
        ChordNode pred = this.findPredecessor(this, new Identifier(-1, ident_id));
        pred.updateFingerTable(this, i);
      }
    }

    /*
    int m = getNetwork().getNbits();
    IdentifierCircle<Identifier> circle = getNetwork().getIdentifierCircle();

    for (int i = 1; i <= m; i++) {
      	int offset = 1 << (i - 1);
        int targetIndex = this.id().getIndex() - offset;
        Identifier idToFind = circle.getIdentifierAt(targetIndex);
        ChordNode p = this.findPredecessor(this, idToFind);
        p.updateFingerTable(this, i);
    }
    */
  }

  /**
   * If node {@code s} is the i-th finger of this node, update this node's finger table with {@code s}
   *
   * Defined in [1], Figure 6
   *
   * @param s The should-be i-th finger of this node
   * @param i The index of {@code s} in this node's finger table
   */
  @Override
  public void updateFingerTable(ChordNode s, int i) {
    /* TODO ( done): Implementation required. */
    finger().node(i).ifPresent(current -> {
        if (current == this) {              
            this.fingerTable.setNode(i, s);
            ChordNode p = this.predecessor();
            if (p != null && p != s) {
                p.updateFingerTable(s, i);
            }
            return;
        }

        IdentifierCircularInterval interval =
                IdentifierCircularInterval.createRightOpen(this.id(), current.id());

        if (interval.contains(s.id())) {
            this.fingerTable.setNode(i, s);
            ChordNode p = this.predecessor();
            if (p != null && p != s) {
                p.updateFingerTable(s, i);
            }
        }
    });
  }

  /**
   * Called by {@code nprime} if it thinks it might be this {@link ChordNode}'s predecessor. Updates predecessor
   * pointers accordingly, if required.
   *
   * Defined in [1], Figure 7
   *
   * @param nprime The alleged predecessor of this {@link ChordNode}
   */
  @Override
  public void notify(ChordNode nprime) {
    if (this.status() == NodeStatus.OFFLINE || this.status() == NodeStatus.JOINING) return;

    /* TODO(done): Implementation required. Hint: Null check on predecessor! */
    ChordNode pred = this.predecessor();
    if (pred == null) {
      this.setPredecessor(nprime);
      return;
    }

    // Wenn nprime in (pred, this) liegt, ist er „näher“
    IdentifierCircularInterval interval =
        IdentifierCircularInterval.createOpen(pred.id(), this.id());
    if (interval.contains(nprime.id())) {
      this.setPredecessor(nprime);
    }

  }

  /**
   * Called periodically in order to refresh entries in this {@link ChordNode}'s {@link FingerTable}.
   *
   * Defined in [1], Figure 7
   */
  @Override
  public void fixFingers() {
    if (this.status() == NodeStatus.OFFLINE || this.status() == NodeStatus.JOINING) return;

    /* TODO(done): Implementation required */
    int m = getNetwork().getNbits();
    Random rnd = new Random();
    int i = 1 + rnd.nextInt(m);        // zufälligen Finger fixen

    IdentifierCircle<Identifier> circle = getNetwork().getIdentifierCircle();
    Identifier start = circle.getIdentifierAt(finger().start(i));
    ChordNode succ = this.findSuccessor(this, start);
    this.fingerTable.setNode(i, succ);
  }

  /**
   * Called periodically in order to verify this node's immediate successor and inform it about this
   * {@link ChordNode}'s presence,
   *
   * Defined in [1], Figure 7
   */
  @Override
  public void stabilize() {
    if (this.status() == NodeStatus.OFFLINE || this.status() == NodeStatus.JOINING) return;

    /* TODO(done): Implementation required.*/
    ChordNode succ = this.successor();
    if (succ == null) {
      // sollte eigentlich nie passieren — recover über uns selbst
      this.fingerTable.setNode(1, this);
      return;
    }

    ChordNode x = succ.predecessor();
    // prüfen ob x zwischen uns und unserem aktuellen successor liegt
    if (x != null) {
      IdentifierCircularInterval interval =
          IdentifierCircularInterval.createOpen(this.id(), succ.id());
      if (interval.contains(x.id())) {
        // x ist „besserer“ successor
        this.fingerTable.setNode(1, x);
        succ = x;
      }
    }
    // successor informieren
    succ.notify(this);
  }

  /**
   * Called periodically in order to check activity of this {@link ChordNode}'s predecessor.
   *
   * Not part of [1]. Required for dynamic network to handle node failure.
   */
  @Override
  public void checkPredecessor() {
    if (this.status() == NodeStatus.OFFLINE || this.status() == NodeStatus.JOINING) return;

    ChordNode pred = this.predecessor();
    if (pred != null && pred.status() == NodeStatus.OFFLINE) {
      this.setPredecessor(null);
    }
  }

  /**
   * Called periodically in order to check activity of this {@link ChordNode}'s successor.
   *
   * Not part of [1]. Required for dynamic network to handle node failure.
   */
  @Override
  public void checkSuccessor() {
    if (this.status() == NodeStatus.OFFLINE || this.status() == NodeStatus.JOINING) return;
    /* TODO(done): Implementation required. Hint: Null check on predecessor! */
    ChordNode succ = this.successor();
    if (succ != null && succ.status() != NodeStatus.OFFLINE) {
      return; // alles ok
    }

    // successor ist tot → versuch aus der Finger-Tabelle einen neuen zu nehmen
    int m = getNetwork().getNbits();
    for (int i = 2; i <= m; i++) {
      ChordNode cand = finger().node(i).orElse(null);
      if (cand != null && cand != this && cand.status() != NodeStatus.OFFLINE) {
        this.fingerTable.setNode(1, cand);
        return;
      }
    }

    // worst case — wir zeigen auf uns selbst
    this.fingerTable.setNode(1, this);
  }

  /**
   * Performs a lookup for where the data with the provided key should be stored.
   *
   * @return Node in which to store the data with the provided key.
   */
  @Override
  protected ChordNode lookupNodeForItem(String key) {
    /* TODO (done): Implementation required. Hint: Null check on predecessor! */
	int hashed = getNetwork().getHashFunction().hash(key);
    IdentifierCircle<Identifier> circle = getNetwork().getIdentifierCircle();
    Identifier id = circle.getIdentifierAt(hashed);
    return this.findSuccessor(this, id);
  }

  @Override
  public String toString() {
    return String.format("ChordPeer{id=%d}", this.id().getIndex());
  }
}
