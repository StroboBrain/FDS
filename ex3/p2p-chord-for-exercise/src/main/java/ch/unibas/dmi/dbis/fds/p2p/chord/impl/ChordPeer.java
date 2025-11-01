package ch.unibas.dmi.dbis.fds.p2p.chord.impl;

import ch.unibas.dmi.dbis.fds.p2p.chord.api.*;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.ChordNetwork;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.data.Identifier;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.data.IdentifierCircle;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.data.IdentifierCircularInterval;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.math.CircularInterval;

import java.util.Random;

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
  //example: with nodes(1, 8, 14) and we search the id 12, we get the node 8 first (with findPredecessor) and then we can do node.successor()
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
   * @param id The {@link Identifier} for which to lookup the predecessor. Does not need to be the ID of an actual {@link ChordNode}!
   * @return The predecessor of or the node {@code of} from this {@link ChordNode}'s point of view
   */
  @Override
  public ChordNode findPredecessor(ChordNode caller, Identifier id) {
    /* TODO(done): Implementation required. */
    ChordNode n = this;
    while (!IdentifierCircularInterval.createLeftOpen(n.getIdentifier(), n.successor().getIdentifier()).contains(id)) {
      n = n.closestPrecedingFinger(caller, id);
    }return n;
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
    int m = fingerTable.size();
    for (int i = m; i >= 1; i--) {
        var opt = finger().node(i);     //here we need to ensure that we don't get a nullpointer exception
        if (opt.isPresent()) {
            ChordNode f = opt.get();
            if (IdentifierCircularInterval
                    .createOpen(this.getIdentifier(), id)
                    .contains(f.getIdentifier())) {
                return f;
            }
        }
    }
    return this;
  }

  private void moveKeysFromSuccessor() {
    ChordNode succ = this.successor();
    if (succ == null || succ == this) {
        return;
    }

    ChordNode pred = this.predecessor();
    if (pred == null) {
        return;
    }

    //(pred(n), n]
    IdentifierCircularInterval myRange =
            IdentifierCircularInterval.createLeftOpen(pred.getIdentifier(), this.getIdentifier());

    //Keys vom Nachfolger holen
    AbstractChordPeer succPeer = (AbstractChordPeer) succ;
    var keys = succPeer.keys();

    IdentifierCircle circle = new IdentifierCircle(getNetwork().getNbits());

    for (String k : keys) {
        int h = getNetwork().getHashFunction().hash(k);
        Identifier keyId = circle.getIdentifierAt(h);

        if (myRange.contains(keyId)) {
            succPeer.delete(this, k).ifPresent(v -> this.store(this, k, v));
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
      moveKeysFromSuccessor();
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
      this.fingerTable.setNode(1, nprime.findSuccessor(this,this));
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
    IdentifierCircle circle = new IdentifierCircle(getNetwork().getNbits());

    //finger[1].node = n'.find_successor(finger[1].start);
    Identifier start1 = circle.getIdentifierAt(finger().start(1));
    ChordNode succ = nprime.findSuccessor(this, start1);
    this.fingerTable.setNode(1, succ);

    //predecessor = successor.predecessor;
    this.setPredecessor(succ.predecessor());

    //successor.predecessor = n;
    succ.setPredecessor(this);

    int m = finger().size();
    for (int i = 1; i < m; i++) {
        Identifier startNext = circle.getIdentifierAt(finger().start(i + 1));
        ChordNode prevFingerNode = finger().node(i).get();   //finger[i].node

        var interval = IdentifierCircularInterval
                .createRightOpen(this.getIdentifier(), prevFingerNode.getIdentifier());

        if (interval.contains(startNext)) {
            fingerTable.setNode(i + 1, prevFingerNode);
        } else {
            fingerTable.setNode(i + 1, nprime.findSuccessor(this, startNext));
        }
    }

  }

  /**
   * Updates all {@link ChordNode} whose {@link FingerTable} should refer to this {@link ChordNode}.
   *
   * Defined in [1], Figure 6
   */
  private void updateOthers() {
    /* TODO(done): Implementation required. */
    int m = finger().size();                          // = nbits
    IdentifierCircle circle = new IdentifierCircle(getNetwork().getNbits());
    int ringSize = (int) Math.pow(2, m);

    for (int i = 1; i <= m; i++) {
        int offset = (int) Math.pow(2, i - 1);        //2^{i-1}

        //(n - 2^{i-1}) mod 2^m
        int idx = (this.id().getIndex() - offset) % ringSize;
        if (idx < 0) {
            idx += ringSize;
        }

        Identifier id = circle.getIdentifierAt(idx);

        //p = find_predecessor(n - 2^{i-1});
        ChordNode p = this.findPredecessor(this, id);

        //p.update_finger_table(n, i);
        p.updateFingerTable(this, i);
    }
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
    finger().node(i).ifPresent(node -> {
      /* TODO(done): Implementation required. */
      // if (s ∈ [n, finger[i].node))
        boolean inInterval = IdentifierCircularInterval
                .createRightOpen(this.getIdentifier(), node.getIdentifier())
                .contains(s.getIdentifier());

        IdentifierCircle circle = new IdentifierCircle(getNetwork().getNbits());
        Identifier fingerStart = circle.getIdentifierAt(finger().start(i));

        boolean startInRange =
        IdentifierCircularInterval
            .createRightOpen(this.getIdentifier(), s.getIdentifier())
            .contains(fingerStart);        

        if (inInterval && startInRange) { //was not like this in Paper!! (startInRange)
            //finger[i].node = s;
            this.fingerTable.setNode(i, s);

            //p = predecessor; p.update_finger_table(s, i);
            ChordNode p = this.predecessor();
            if (p != null && p != s) {
                p.updateFingerTable(s, i);
            }
        }
    });

    if (finger().node(i).isEmpty()) {
        this.fingerTable.setNode(i, s);
        ChordNode p = this.predecessor();
        if (p != null && p != s) {
            p.updateFingerTable(s, i);
        }
    }
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
    //if (predecessor is nil or n' ∈ (predecessor, n))
    if (this.predecessor() == null ||
        IdentifierCircularInterval
                .createOpen(this.predecessor().getIdentifier(), this.getIdentifier())
                .contains(nprime.getIdentifier())) {
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
    int m = finger().size();
    if (m <= 1) return;

    //i = random index > 1 into finger[];
    int i = 2 + new Random().nextInt(m - 1);   // 2..m

    IdentifierCircle circle = new IdentifierCircle(getNetwork().getNbits());
    Identifier start = circle.getIdentifierAt(finger().start(i));

    //finger[i].node = find_successor(finger[i].start);
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
    if (succ == null) return;

    //x = successor.predecessor;
    ChordNode x = succ.predecessor();

    //if (x ∈ (n, successor))
    if (x != null &&
        IdentifierCircularInterval
                .createOpen(this.getIdentifier(), succ.getIdentifier())
                .contains(x.getIdentifier())) {
        // successor = x;
        this.fingerTable.setNode(1, x);
        succ = x;
    }

    //successor.notify(n);
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

    /* TODO(done): Implementation required. Hint: Null check on predecessor! */
    ChordNode p = this.predecessor();
    if (p == null) return;

    if (((AbstractChordPeer) p).status() == NodeStatus.OFFLINE) {
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
    if (succ == null) {
        this.fingerTable.setNode(1, this);
        return;
    }

    if (((AbstractChordPeer) succ).status() == NodeStatus.OFFLINE) {
        this.fingerTable.setNode(1, this);
    }
  }

  /**
   * Performs a lookup for where the data with the provided key should be stored.
   *
   * @return Node in which to store the data with the provided key.
   */
  @Override
  protected ChordNode lookupNodeForItem(String key) {
    /* TODO(done): Implementation required. Hint: Null check on predecessor! */
    int h = getNetwork().getHashFunction().hash(key);
    IdentifierCircle circle = new IdentifierCircle(getNetwork().getNbits());
    Identifier keyId = circle.getIdentifierAt(h);
    return this.findSuccessor(this, keyId);
  }

  @Override
  public String toString() {
    return String.format("ChordPeer{id=%d}", this.id().getIndex());
  }
}
