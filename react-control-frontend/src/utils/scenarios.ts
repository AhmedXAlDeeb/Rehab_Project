export const ID_TO_GESTURE_MAP: Record<number, string> = {
  0: "rest",
  1: "b1_thumb_up", 2: "b2_index_middle_ext", 3: "b3_ring_little_flex", 4: "b4_thumb_opp_little",
  5: "b5_all_abduction", 6: "b6_fist", 7: "b7_pointing", 8: "b8_adduction_extended",
  9: "b9_wrist_sup_mid", 10: "b10_wrist_pro_mid", 11: "b11_wrist_sup_little", 12: "b12_wrist_pro_little",
  13: "b13_wrist_flexion", 14: "b14_wrist_extension", 15: "b15_wrist_radial", 16: "b16_wrist_ulnar",
  17: "b17_wrist_ext_closed",
  18: "c1_large_diameter", 19: "c2_small_diameter", 20: "c3_fixed_hook", 21: "c4_index_ext_grasp",
  22: "c5_medium_wrap", 23: "c6_ring_grasp", 24: "c7_prismatic_four", 25: "c8_stick_grasp",
  26: "c9_writing_tripod", 27: "c10_power_sphere", 28: "c11_three_finger_sphere", 29: "c12_precision_sphere",
  30: "c13_tripod", 31: "c14_prismatic_pinch", 32: "c15_tip_pinch", 33: "c16_quadpod",
  34: "c17_lateral", 35: "c18_parallel_ext", 36: "c19_extension_type", 37: "c20_power_disk",
  38: "c21_bottle_tripod", 39: "c22_screw_stick", 40: "c23_cut_knife",
  41: "d1_little_flex", 42: "d2_ring_flex", 43: "d3_middle_flex", 44: "d4_index_flex",
  45: "d5_thumb_abd", 46: "d6_thumb_flex", 47: "d7_index_little_flex", 48: "d8_ring_middle_flex",
  49: "d9_index_thumb_flex",
};

export const SCENARIOS = [
  {
    name: "Hand Warmup (Fist & Point)",
    motions: [0, 6, 7, 0],
  },
  {
    name: "Grasping Drill (Large & Small)",
    motions: [18, 19, 0],
  },
  {
    name: "Wrist Control (Flex/Ext)",
    motions: [13, 14, 0],
  }
];