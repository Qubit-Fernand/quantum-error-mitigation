OPENQASM 3;
include "stdgates.inc";
gate rzz_5523845808(_gate_p_0) _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
  rz(-0.05) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
}
gate exp(it IIIZZ) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rzz_5523845808(-0.05) _gate_q_0, _gate_q_1;
}
gate rzz_5523341120(_gate_p_0) _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
  rz(-0.05) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
}
gate exp(it IIZZI) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rzz_5523341120(-0.05) _gate_q_1, _gate_q_2;
}
gate rzz_5525001840(_gate_p_0) _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
  rz(-0.05) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
}
gate exp(it IZZII) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rzz_5525001840(-0.05) _gate_q_2, _gate_q_3;
}
gate rzz_5525002704(_gate_p_0) _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
  rz(-0.05) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
}
gate exp(it ZZIII) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rzz_5525002704(-0.05) _gate_q_3, _gate_q_4;
}
gate exp(it IIIIX) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rx(-0.1) _gate_q_0;
}
gate exp(it IIIXI) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rx(-0.1) _gate_q_1;
}
gate exp(it IIXII) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rx(-0.1) _gate_q_2;
}
gate exp(it IXIII) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rx(-0.1) _gate_q_3;
}
gate exp(it XIIII) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rx(-0.1) _gate_q_4;
}
gate rzz_5523632336(_gate_p_0) _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
  rz(-0.05) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
}
gate exp(it IIIZZ)_5524973456 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rzz_5523632336(-0.05) _gate_q_0, _gate_q_1;
}
gate rzz_5523340640(_gate_p_0) _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
  rz(-0.05) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
}
gate exp(it IIZZI)_5523866720 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rzz_5523340640(-0.05) _gate_q_1, _gate_q_2;
}
gate rzz_5523337280(_gate_p_0) _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
  rz(-0.05) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
}
gate exp(it IZZII)_5523837520 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rzz_5523337280(-0.05) _gate_q_2, _gate_q_3;
}
gate rzz_5523339968(_gate_p_0) _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
  rz(-0.05) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
}
gate exp(it ZZIII)_5523339296 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rzz_5523339968(-0.05) _gate_q_3, _gate_q_4;
}
gate exp(it IIIIX)_5523338624 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rx(-0.1) _gate_q_0;
}
gate exp(it IIIXI)_5523340688 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rx(-0.1) _gate_q_1;
}
gate exp(it IIXII)_5523848592 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rx(-0.1) _gate_q_2;
}
gate exp(it IXIII)_5520141904 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rx(-0.1) _gate_q_3;
}
gate exp(it XIIII)_5523360592 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  rx(-0.1) _gate_q_4;
}
qubit[5] q;
exp(it IIIZZ) q[0], q[1], q[2], q[3], q[4];
exp(it IIZZI) q[0], q[1], q[2], q[3], q[4];
exp(it IZZII) q[0], q[1], q[2], q[3], q[4];
exp(it ZZIII) q[0], q[1], q[2], q[3], q[4];
exp(it IIIIX) q[0], q[1], q[2], q[3], q[4];
exp(it IIIXI) q[0], q[1], q[2], q[3], q[4];
exp(it IIXII) q[0], q[1], q[2], q[3], q[4];
exp(it IXIII) q[0], q[1], q[2], q[3], q[4];
exp(it XIIII) q[0], q[1], q[2], q[3], q[4];
exp(it IIIZZ)_5524973456 q[0], q[1], q[2], q[3], q[4];
exp(it IIZZI)_5523866720 q[0], q[1], q[2], q[3], q[4];
exp(it IZZII)_5523837520 q[0], q[1], q[2], q[3], q[4];
exp(it ZZIII)_5523339296 q[0], q[1], q[2], q[3], q[4];
exp(it IIIIX)_5523338624 q[0], q[1], q[2], q[3], q[4];
exp(it IIIXI)_5523340688 q[0], q[1], q[2], q[3], q[4];
exp(it IIXII)_5523848592 q[0], q[1], q[2], q[3], q[4];
exp(it IXIII)_5520141904 q[0], q[1], q[2], q[3], q[4];
exp(it XIIII)_5523360592 q[0], q[1], q[2], q[3], q[4];
