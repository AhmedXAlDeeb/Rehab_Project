import numpy as np

# ─── MyoHand: 39 muscle actuators ────────────────────────────────────────────
#
# Actuator order from myohand_assets.xml (EXACT — do not reorder):
#
#  idx  name       role
#  ---  ---------  --------------------------------------------------
#   0   ECRL       Wrist extension + radial deviation
#   1   ECRB       Wrist extension + radial deviation
#   2   ECU        Wrist extension + ulnar deviation
#   3   FCR        Wrist flexion  + radial deviation
#   4   FCU        Wrist flexion  + ulnar deviation
#   5   PL         Wrist flexion (palmaris longus)
#   6   PT         Forearm pronation
#   7   PQ         Forearm pronation (distal)
#   8   FDS5       Little  PIP flexion  (superficialis)
#   9   FDS4       Ring    PIP flexion
#  10   FDS3       Middle  PIP flexion
#  11   FDS2       Index   PIP flexion
#  12   FDP5       Little  DIP flexion  (profundus)
#  13   FDP4       Ring    DIP flexion
#  14   FDP3       Middle  DIP flexion
#  15   FDP2       Index   DIP flexion
#  16   EDC5       Little  MCP/PIP/DIP extension
#  17   EDC4       Ring    MCP/PIP/DIP extension
#  18   EDC3       Middle  MCP/PIP/DIP extension
#  19   EDC2       Index   MCP/PIP/DIP extension
#  20   EDM        Little  MCP extension (extensor digiti minimi)
#  21   EIP        Index   MCP extension (extensor indicis proprius)
#  22   EPL        Thumb   IP extension  + adduction
#  23   EPB        Thumb   MCP extension + abduction
#  24   FPL        Thumb   IP flexion
#  25   APL        Thumb   CMC abduction (abductor pollicis longus)
#  26   OP         Thumb   opposition    (opponens pollicis)
#  27   RI2        Index   MCP abduction (radial interosseous)
#  28   LU_RB2     Index   MCP flexion + IP ext (lumbrical/radial)
#  29   UI_UB2     Index   MCP adduction (ulnar interosseous)
#  30   RI3        Middle  MCP abduction
#  31   LU_RB3     Middle  MCP flexion + IP ext
#  32   UI_UB3     Middle  MCP adduction
#  33   RI4        Ring    MCP abduction
#  34   LU_RB4     Ring    MCP flexion + IP ext
#  35   UI_UB4     Ring    MCP adduction
#  36   RI5        Little  MCP abduction
#  37   LU_RB5     Little  MCP flexion + IP ext
#  38   UI_UB5     Little  MCP adduction
#
# Activation values: [0.0, 1.0]  — 0 = relaxed, 1 = fully contracted
# ─────────────────────────────────────────────────────────────────────────────

def _a(*vals):
    """Build a 39-element activation array from provided values, padding with zeros."""
    arr = np.zeros(39)
    for i, v in enumerate(vals):
        if i < 39:
            arr[i] = float(v)
    return arr

# Shorthand column labels (used in comments below):
# [ECRL ECRB ECU  FCR  FCU  PL   PT   PQ ]  indices 0-7   wrist / forearm
# [FDS5 FDS4 FDS3 FDS2]                      indices 8-11  finger PIP flex
# [FDP5 FDP4 FDP3 FDP2]                      indices 12-15 finger DIP flex
# [EDC5 EDC4 EDC3 EDC2 EDM  EIP ]            indices 16-21 finger extension
# [EPL  EPB  FPL  APL  OP  ]                 indices 22-26 thumb
# [RI2  LU2  UI2  RI3  LU3  UI3  RI4  LU4  UI4  RI5  LU5  UI5]
#                                             indices 27-38 intrinsics


# ─── Rest ─────────────────────────────────────────────────────────────────────

REST = _a()


# ─── Exercise A: Individual finger movements ──────────────────────────────────

# A1  Index finger flexion
#     FDS2(11) + FDP2(15) flex PIP+DIP; EIP(21) off; LU_RB2(28) assists MCP
A1_INDEX_FLEXION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  # 0-7  wrist/forearm neutral
    0.0, 0.0, 0.0, 0.8,                        # 8-11 FDS2 on
    0.0, 0.0, 0.0, 0.8,                        # 12-15 FDP2 on
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,             # 16-21 extensors off
    0.0, 0.0, 0.0, 0.0, 0.0,                  # 22-26 thumb neutral
    0.0, 0.7, 0.0,                             # 27-29 LU_RB2 assists index MCP flex
    0.0, 0.0, 0.0,                             # 30-32
    0.0, 0.0, 0.0,                             # 33-35
    0.0, 0.0, 0.0,                             # 36-38
)

# A2  Index finger extension
#     EDC2(19) + EIP(21) extend; FDS2/FDP2 off
A2_INDEX_EXTENSION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.8, 0.0, 0.8,  # EDC2(19) + EIP(21)
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# A3  Middle finger flexion
#     FDS3(10) + FDP3(14); LU_RB3(31) assists MCP
A3_MIDDLE_FLEXION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.8, 0.0,   # FDS3(10)
    0.0, 0.0, 0.8, 0.0,   # FDP3(14)
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.7, 0.0,         # LU_RB3(31)
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# A4  Middle finger extension
#     EDC3(18) extends
A4_MIDDLE_EXTENSION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.8, 0.0, 0.0, 0.0,  # EDC3(18)
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# A5  Ring finger flexion
#     FDS4(9) + FDP4(13); LU_RB4(34) assists MCP
A5_RING_FLEXION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.8, 0.0, 0.0,   # FDS4(9)
    0.0, 0.8, 0.0, 0.0,   # FDP4(13)
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.7, 0.0,         # LU_RB4(34)
    0.0, 0.0, 0.0,
)

# A6  Ring finger extension
#     EDC4(17)
A6_RING_EXTENSION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.8, 0.0, 0.0, 0.0, 0.0,  # EDC4(17)
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# A7  Little finger flexion
#     FDS5(8) + FDP5(12) + EDM assists MCP via LU_RB5(37)
A7_LITTLE_FLEXION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.8, 0.0, 0.0, 0.0,   # FDS5(8)
    0.8, 0.0, 0.0, 0.0,   # FDP5(12)
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.7, 0.0,         # LU_RB5(37)
)

# A8  Little finger extension
#     EDC5(16) + EDM(20)
A8_LITTLE_EXTENSION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.8, 0.0, 0.0, 0.0, 0.8, 0.0,  # EDC5(16) + EDM(20)
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# A9  Thumb adduction (toward palm)
#     EPL(22) adducts + extends IP; OP(26) assists; APL(25) low
A9_THUMB_ADDUCTION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.0, 0.0, 0.0, 0.4,  # EPL(22) + OP(26)
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# A10 Thumb abduction (away from palm)
#     APL(25) abducts CMC; EPB(23) assists MCP extension + abduction
A10_THUMB_ABDUCTION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.7, 0.0, 0.8, 0.0,  # EPB(23) + APL(25)
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# A11 Thumb flexion (curl into palm)
#     FPL(24) flexes IP; OP(26) flexes CMC and palmarises thumb
A11_THUMB_FLEXION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.8, 0.0, 0.6,  # FPL(24) + OP(26)
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# A12 Thumb extension (straighten / retract)
#     EPL(22) extends IP + adducts; EPB(23) extends MCP; APL(25) retracts CMC
A12_THUMB_EXTENSION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.6, 0.0, 0.5, 0.0,  # EPL(22) + EPB(23) + APL(25)
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)


# ─── Exercise B: Combined / wrist movements ────────────────────────────────────

# B1  Thumb up
#     Thumb extended outward; all four fingers curled into palm
B1_THUMB_UP = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.7, 0.7, 0.7,   # FDS5-FDS2: all PIP curled
    0.7, 0.7, 0.7, 0.7,   # FDP5-FDP2: all DIP curled
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.6, 0.5, 0.0, 0.6, 0.0,  # EPL(22)+EPB(23) extend thumb; APL(25) abducts
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B2  Index + middle extended, ring + little curled (peace / scissors)
B2_INDEX_MIDDLE_EXT = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.7, 0.0, 0.0,   # FDS5(8)+FDS4(9) curl ring+little; index+mid off
    0.7, 0.7, 0.0, 0.0,   # FDP5(12)+FDP4(13)
    0.0, 0.0, 0.8, 0.8, 0.0, 0.8,  # EDC3(18)+EDC2(19)+EIP(21) extend mid+idx
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B3  Ring + little curled, index + middle extended (reverse peace)
B3_RING_LITTLE_FLEX = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.8, 0.8, 0.0, 0.0,   # FDS5+FDS4 curl ring+little
    0.8, 0.8, 0.0, 0.0,   # FDP5+FDP4
    0.0, 0.0, 0.7, 0.7, 0.0, 0.7,  # EDC3+EDC2+EIP extend mid+idx
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B4  Thumb opposing base of little finger (full opposition)
#     OP(26) strongly; FPL(24); all fingers lightly curled
B4_THUMB_OPP_LITTLE = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.3, 0.3, 0.3, 0.3,
    0.2, 0.2, 0.2, 0.2,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.3, 0.0, 0.6, 0.5, 0.9,  # EPL(22)+FPL(24)+APL(25)+OP(26)
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B5  Abduction of all fingers (spread)
#     RI2(27)+RI3(30)+RI5(36) abduct; UI_UB* relax
B5_ALL_ABDUCTION = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.5, 0.0, 0.6, 0.0,  # EPB(23)+APL(25) spread thumb
    0.7, 0.0, 0.0,  # RI2(27)
    0.7, 0.0, 0.0,  # RI3(30)
    0.7, 0.0, 0.0,  # RI4(33)
    0.7, 0.0, 0.0,  # RI5(36)
)

# B6  Fist (all fingers + thumb fully curled)
B6_FIST = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.9, 0.9, 0.9, 0.9,   # FDS5-FDS2
    0.9, 0.9, 0.9, 0.9,   # FDP5-FDP2
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.8, 0.0, 0.6,  # FPL(24)+OP(26) curl thumb
    0.0, 0.5, 0.0,  # LU_RB2(28) assists index MCP
    0.0, 0.5, 0.0,  # LU_RB3(31)
    0.0, 0.5, 0.0,  # LU_RB4(34)
    0.0, 0.5, 0.0,  # LU_RB5(37)
)

# B7  Pointing (index extended, all others curled)
B7_POINTING = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.8, 0.8, 0.8, 0.0,   # FDS5+FDS4+FDS3 curl little+ring+middle
    0.8, 0.8, 0.8, 0.0,   # FDP5+FDP4+FDP3
    0.0, 0.0, 0.0, 0.7, 0.0, 0.7,  # EDC2(19)+EIP(21) extend index
    0.0, 0.0, 0.5, 0.0, 0.4,  # FPL(24)+OP(26) keep thumb tucked
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B8  Adduction of extended fingers (fingers together, flat)
#     All extensors on; UI_UB* adduct; RI* relax
B8_ADDUCTION_EXTENDED = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # all EDC + EDM + EIP
    0.0, 0.4, 0.0, 0.0, 0.0,  # EPB(23) extend thumb flat
    0.0, 0.0, 0.5,  # UI_UB2(29)
    0.0, 0.0, 0.5,  # UI_UB3(32)
    0.0, 0.0, 0.5,  # UI_UB4(35)
    0.0, 0.0, 0.5,  # UI_UB5(38)
)

# B9  Wrist supination, fingers neutral (axis: middle finger)
#     No PT/PQ — those are pronators. Supination is passive here (no direct
#     supinator muscle in this model; PT/PQ(6,7) off, wrist neutral)
B9_WRIST_SUP_MID = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B10 Wrist pronation, fingers neutral (axis: middle finger)
#     PT(6) + PQ(7) pronate forearm
B10_WRIST_PRO_MID = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.6,  # PT(6)+PQ(7)
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B11 Wrist supination + ulnar deviation (axis: little finger)
#     ECU(2) deviates ulnar; supination passive (PT/PQ off)
B11_WRIST_SUP_LITTLE = _a(
    0.0, 0.0, 0.5, 0.0, 0.3, 0.0, 0.0, 0.0,  # ECU(2)+FCU(4) ulnar
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B12 Wrist pronation + ulnar deviation (axis: little finger)
#     PT(6)+PQ(7) pronate; ECU(2)+FCU(4) deviate ulnar
B12_WRIST_PRO_LITTLE = _a(
    0.0, 0.0, 0.5, 0.0, 0.3, 0.0, 0.8, 0.6,  # ECU(2)+FCU(4)+PT(6)+PQ(7)
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B13 Wrist flexion
#     FCR(3)+FCU(4)+PL(5)
B13_WRIST_FLEXION = _a(
    0.0, 0.0, 0.0, 0.8, 0.7, 0.6, 0.0, 0.0,  # FCR(3)+FCU(4)+PL(5)
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B14 Wrist extension
#     ECRL(0)+ECRB(1)+ECU(2)
B14_WRIST_EXTENSION = _a(
    0.7, 0.7, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0,  # ECRL(0)+ECRB(1)+ECU(2)
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B15 Wrist radial deviation
#     ECRL(0)+ECRB(1) extend-radial; FCR(3) flex-radial; balance gives pure radial
B15_WRIST_RADIAL = _a(
    0.6, 0.6, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0,  # ECRL(0)+ECRB(1)+FCR(3)
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B16 Wrist ulnar deviation
#     ECU(2)+FCU(4); balance gives pure ulnar
B16_WRIST_ULNAR = _a(
    0.0, 0.0, 0.6, 0.0, 0.6, 0.0, 0.0, 0.0,  # ECU(2)+FCU(4)
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# B17 Wrist extension with closed fist
#     ECRL+ECRB+ECU extend wrist; all FDS/FDP curl fingers
B17_WRIST_EXT_CLOSED = _a(
    0.7, 0.7, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.9, 0.9, 0.9, 0.9,
    0.9, 0.9, 0.9, 0.9,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.8, 0.0, 0.5,  # FPL+OP curl thumb
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)


# ─── Exercise C: Grasps ───────────────────────────────────────────────────────

# C1  Large diameter grasp (cylinder ~75mm, e.g. mug)
C1_LARGE_DIAMETER = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.6, 0.6, 0.6, 0.6,
    0.5, 0.5, 0.5, 0.5,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.6, 0.3, 0.5,  # FPL+APL+OP wrap thumb
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
)

# C2  Small diameter grasp (power grip ~25mm, e.g. hammer)
C2_SMALL_DIAMETER = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.9, 0.9, 0.9, 0.9,
    0.9, 0.9, 0.9, 0.9,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.8, 0.3, 0.7,
    0.0, 0.5, 0.0,
    0.0, 0.5, 0.0,
    0.0, 0.5, 0.0,
    0.0, 0.5, 0.0,
)

# C3  Fixed hook grasp (PIP+DIP curled, MCP near-neutral; e.g. briefcase handle)
#     FDS/FDP create hook; lumbricals extend MCP slightly
C3_FIXED_HOOK = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.8, 0.8, 0.8, 0.8,   # FDS: PIP curl
    0.8, 0.8, 0.8, 0.8,   # FDP: DIP curl
    0.3, 0.3, 0.3, 0.3, 0.0, 0.3,  # EDC*+EIP partially extend MCP
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.6, 0.0,  # LU_RB2 extends MCP
    0.0, 0.6, 0.0,
    0.0, 0.6, 0.0,
    0.0, 0.6, 0.0,
)

# C4  Index finger extension grasp (index straight, others curled + thumb)
C4_INDEX_EXT_GRASP = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.7, 0.7, 0.0,   # little+ring+middle curled; index off
    0.7, 0.7, 0.7, 0.0,
    0.0, 0.0, 0.0, 0.6, 0.0, 0.6,  # EDC2+EIP extend index
    0.0, 0.0, 0.5, 0.3, 0.5,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# C5  Medium wrap (all fingers moderately curled, thumb wrapped)
C5_MEDIUM_WRAP = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.7, 0.7, 0.7,
    0.7, 0.7, 0.7, 0.7,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.7, 0.4, 0.6,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
)

# C6  Ring grasp (circular; thumb opposes fingers, all moderately flexed)
C6_RING_GRASP = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.5, 0.5, 0.5, 0.5,
    0.4, 0.4, 0.4, 0.4,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.2, 0.0, 0.6, 0.4, 0.7,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
)

# C7  Prismatic four-finger grasp (four fingers adducted + slightly curled)
C7_PRISMATIC_FOUR = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.5, 0.5, 0.5, 0.5,
    0.4, 0.4, 0.4, 0.4,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.4, 0.3, 0.5,
    0.0, 0.0, 0.5,  # UI_UB2 adducts
    0.0, 0.0, 0.5,
    0.0, 0.0, 0.5,
    0.0, 0.0, 0.5,
)

# C8  Stick grasp (cylindrical grip on thin rod)
C8_STICK_GRASP = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.7, 0.7, 0.7,
    0.6, 0.6, 0.6, 0.6,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.6, 0.3, 0.5,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
)

# C9  Writing tripod grasp (pen: thumb+index+middle; ring+little tucked)
C9_WRITING_TRIPOD = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.8, 0.8, 0.3, 0.3,   # little+ring curled; middle+index light
    0.8, 0.8, 0.3, 0.3,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.2, 0.0, 0.5, 0.4, 0.6,  # EPL+FPL+APL+OP stabilise thumb
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# C10 Power sphere grasp (ball ~90mm, e.g. baseball)
C10_POWER_SPHERE = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.7, 0.7, 0.7,
    0.6, 0.6, 0.6, 0.6,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.7, 0.4, 0.6,
    0.0, 0.5, 0.0,
    0.0, 0.5, 0.0,
    0.0, 0.5, 0.0,
    0.0, 0.5, 0.0,
)

# C11 Three-finger sphere grasp (small ball ~50mm: thumb+index+middle)
C11_THREE_FINGER_SPHERE = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.7, 0.5, 0.5,   # ring+little tucked more
    0.7, 0.7, 0.5, 0.4,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.2, 0.0, 0.6, 0.4, 0.6,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# C12 Precision sphere grasp (~30mm: fingertips, light contact)
C12_PRECISION_SPHERE = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.5, 0.5, 0.4, 0.4,
    0.4, 0.4, 0.4, 0.3,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.3, 0.0, 0.6, 0.4, 0.7,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# C13 Tripod grasp (thumb+index+middle pinch on flat object)
C13_TRIPOD = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.7, 0.4, 0.4,
    0.6, 0.6, 0.3, 0.3,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.3, 0.0, 0.5, 0.4, 0.6,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# C14 Prismatic pinch grasp (flat object, thumb lateral on index)
C14_PRISMATIC_PINCH = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.6, 0.6, 0.4, 0.3,
    0.5, 0.5, 0.3, 0.2,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.5, 0.0, 0.3, 0.0, 0.3,  # EPL adducts thumb to index side
    0.0, 0.0, 0.5,  # UI_UB2 adducts index
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# C15 Tip pinch grasp (thumb tip vs index tip, small object ~10mm)
C15_TIP_PINCH = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.6, 0.6, 0.6, 0.5,
    0.5, 0.5, 0.5, 0.4,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.2, 0.0, 0.7, 0.3, 0.6,  # FPL strong for tip contact
    0.0, 0.4, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# C16 Quadpod grasp (thumb+index+middle+ring; little tucked)
C16_QUADPOD = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.4, 0.4, 0.4,
    0.6, 0.4, 0.4, 0.3,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.3, 0.0, 0.5, 0.4, 0.6,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.0, 0.0,
)

# C17 Lateral grasp (key grip: thumb adducts onto radial side of index)
#     EPL(22) adducts thumb strongly; FDS2/FDP2 flex index; others lightly flexed
C17_LATERAL = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.7, 0.7, 0.4,
    0.6, 0.6, 0.6, 0.4,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.8, 0.0, 0.3, 0.0, 0.3,  # EPL(22) strong adduction to index side
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# C18 Parallel extension grasp (flat extended hand, slight MCP flexion)
C18_PARALLEL_EXT = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0,
    0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # all extensors
    0.0, 0.4, 0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
)

# C19 Extension type grasp (thumb extended, fingers partially curled at MCP)
C19_EXTENSION_TYPE = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.3, 0.3, 0.3, 0.3,
    0.2, 0.2, 0.2, 0.2,
    0.4, 0.4, 0.4, 0.4, 0.0, 0.4,  # extensors partially active
    0.4, 0.4, 0.0, 0.5, 0.0,  # EPL+EPB extend thumb
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
)

# C20 Power disk grasp (flat disk ~100mm, e.g. jar lid)
C20_POWER_DISK = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.5, 0.5, 0.5, 0.5,
    0.5, 0.5, 0.5, 0.5,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.5, 0.4, 0.6,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
    0.0, 0.3, 0.0,
)

# C21 Open a bottle with tripod grasp (thumb+index+middle, slight supination)
#     Same as C9 but fingers apply more force and forearm is neutral->supinated
C21_BOTTLE_TRIPOD = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  # PT/PQ off → supination tendency
    0.8, 0.8, 0.4, 0.4,
    0.8, 0.8, 0.3, 0.3,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.3, 0.0, 0.6, 0.4, 0.7,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)

# C22 Turn a screw (stick grasp + pronation)
#     PT(6)+PQ(7) pronate; all fingers moderately curled
C22_SCREW_STICK = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.7, 0.5,  # PT(6)+PQ(7)
    0.6, 0.6, 0.6, 0.6,
    0.6, 0.6, 0.6, 0.6,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.5, 0.3, 0.5,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
    0.0, 0.4, 0.0,
)

# C23 Cut with knife (index extended, others wrapped around handle + thumb)
C23_CUT_KNIFE = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.7, 0.7, 0.7, 0.0,   # little+ring+middle curled; index off
    0.7, 0.7, 0.7, 0.0,
    0.0, 0.0, 0.0, 0.6, 0.0, 0.6,  # EDC2+EIP extend index
    0.0, 0.0, 0.5, 0.3, 0.5,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)


# ─── Exercise D: Individual finger movements (EMG electrode context) ──────────
# Biomechanically identical to Exercise A equivalents

D1_LITTLE_FLEX    = A7_LITTLE_FLEXION.copy()
D2_RING_FLEX      = A5_RING_FLEXION.copy()
D3_MIDDLE_FLEX    = A3_MIDDLE_FLEXION.copy()
D4_INDEX_FLEX     = A1_INDEX_FLEXION.copy()
D5_THUMB_ABD      = A10_THUMB_ABDUCTION.copy()
D6_THUMB_FLEX     = A11_THUMB_FLEXION.copy()

# D7  Flexion of index + little; middle + ring extended
D7_INDEX_LITTLE_FLEX = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.8, 0.0, 0.0, 0.8,   # FDS5(8)+FDS2(11)
    0.8, 0.0, 0.0, 0.8,   # FDP5(12)+FDP2(15)
    0.0, 0.7, 0.7, 0.0, 0.0, 0.0,  # EDC4(17)+EDC3(18) extend ring+middle
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.5, 0.0,  # LU_RB2
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.5, 0.0,  # LU_RB5
)

# D8  Flexion of ring + middle; index + little extended
D8_RING_MIDDLE_FLEX = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.8, 0.8, 0.0,   # FDS4(9)+FDS3(10)
    0.0, 0.8, 0.8, 0.0,   # FDP4(13)+FDP3(14)
    0.7, 0.0, 0.0, 0.7, 0.7, 0.7,  # EDC5+EDC2+EDM+EIP extend little+index
    0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.5, 0.0,  # LU_RB3
    0.0, 0.5, 0.0,  # LU_RB4
    0.0, 0.0, 0.0,
)

# D9  Flexion of index + thumb; others lightly extended
D9_INDEX_THUMB_FLEX = _a(
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.5, 0.5, 0.5, 0.7,   # others lightly curled; index FDS2(11) strong
    0.5, 0.5, 0.5, 0.7,   # FDP2(15) strong
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.7, 0.3, 0.6,  # FPL(24)+APL(25)+OP(26)
    0.0, 0.6, 0.0,  # LU_RB2
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
)


# ─── Gesture registry ─────────────────────────────────────────────────────────

GESTURES: dict[str, np.ndarray] = {
    "rest": REST,
    # Exercise A
    "a1_index_flexion":    A1_INDEX_FLEXION,
    "a2_index_extension":  A2_INDEX_EXTENSION,
    "a3_middle_flexion":   A3_MIDDLE_FLEXION,
    "a4_middle_extension": A4_MIDDLE_EXTENSION,
    "a5_ring_flexion":     A5_RING_FLEXION,
    "a6_ring_extension":   A6_RING_EXTENSION,
    "a7_little_flexion":   A7_LITTLE_FLEXION,
    "a8_little_extension": A8_LITTLE_EXTENSION,
    "a9_thumb_adduction":  A9_THUMB_ADDUCTION,
    "a10_thumb_abduction": A10_THUMB_ABDUCTION,
    "a11_thumb_flexion":   A11_THUMB_FLEXION,
    "a12_thumb_extension": A12_THUMB_EXTENSION,
    # Exercise B
    "b1_thumb_up":           B1_THUMB_UP,
    "b2_index_middle_ext":   B2_INDEX_MIDDLE_EXT,
    "b3_ring_little_flex":   B3_RING_LITTLE_FLEX,
    "b4_thumb_opp_little":   B4_THUMB_OPP_LITTLE,
    "b5_all_abduction":      B5_ALL_ABDUCTION,
    "b6_fist":               B6_FIST,
    "b7_pointing":           B7_POINTING,
    "b8_adduction_extended": B8_ADDUCTION_EXTENDED,
    "b9_wrist_sup_mid":      B9_WRIST_SUP_MID,
    "b10_wrist_pro_mid":     B10_WRIST_PRO_MID,
    "b11_wrist_sup_little":  B11_WRIST_SUP_LITTLE,
    "b12_wrist_pro_little":  B12_WRIST_PRO_LITTLE,
    "b13_wrist_flexion":     B13_WRIST_FLEXION,
    "b14_wrist_extension":   B14_WRIST_EXTENSION,
    "b15_wrist_radial":      B15_WRIST_RADIAL,
    "b16_wrist_ulnar":       B16_WRIST_ULNAR,
    "b17_wrist_ext_closed":  B17_WRIST_EXT_CLOSED,
    # Exercise C
    "c1_large_diameter":    C1_LARGE_DIAMETER,
    "c2_small_diameter":    C2_SMALL_DIAMETER,
    "c3_fixed_hook":        C3_FIXED_HOOK,
    "c4_index_ext_grasp":   C4_INDEX_EXT_GRASP,
    "c5_medium_wrap":       C5_MEDIUM_WRAP,
    "c6_ring_grasp":        C6_RING_GRASP,
    "c7_prismatic_four":    C7_PRISMATIC_FOUR,
    "c8_stick_grasp":       C8_STICK_GRASP,
    "c9_writing_tripod":    C9_WRITING_TRIPOD,
    "c10_power_sphere":     C10_POWER_SPHERE,
    "c11_three_finger_sphere": C11_THREE_FINGER_SPHERE,
    "c12_precision_sphere": C12_PRECISION_SPHERE,
    "c13_tripod":           C13_TRIPOD,
    "c14_prismatic_pinch":  C14_PRISMATIC_PINCH,
    "c15_tip_pinch":        C15_TIP_PINCH,
    "c16_quadpod":          C16_QUADPOD,
    "c17_lateral":          C17_LATERAL,
    "c18_parallel_ext":     C18_PARALLEL_EXT,
    "c19_extension_type":   C19_EXTENSION_TYPE,
    "c20_power_disk":       C20_POWER_DISK,
    "c21_bottle_tripod":    C21_BOTTLE_TRIPOD,
    "c22_screw_stick":      C22_SCREW_STICK,
    "c23_cut_knife":        C23_CUT_KNIFE,
    # Exercise D
    "d1_little_flex":       D1_LITTLE_FLEX,
    "d2_ring_flex":         D2_RING_FLEX,
    "d3_middle_flex":       D3_MIDDLE_FLEX,
    "d4_index_flex":        D4_INDEX_FLEX,
    "d5_thumb_abd":         D5_THUMB_ABD,
    "d6_thumb_flex":        D6_THUMB_FLEX,
    "d7_index_little_flex": D7_INDEX_LITTLE_FLEX,
    "d8_ring_middle_flex":  D8_RING_MIDDLE_FLEX,
    "d9_index_thumb_flex":  D9_INDEX_THUMB_FLEX,
}

KNOWN_GESTURES = list(GESTURES.keys())


def get_action(gesture_name: str) -> np.ndarray:
    return GESTURES.get(gesture_name, REST).copy()