export const ISL_DB = {
  hello: {
    desc: "Open B-hand, palm out, wave side to side at forehead",
    handshape: "B", loc: "forehead", motion: "wave",
    src: "ISL Dictionary",
    frames: [
      { lx:0,ly:0,la:0,ls:0, rx:.18,ry:-.38,ra:-.1,rs:.9,rhs:"B" },
      { lx:0,ly:0,la:0,ls:0, rx:.10,ry:-.38,ra:.1, rs:.9,rhs:"B" },
      { lx:0,ly:0,la:0,ls:0, rx:.18,ry:-.38,ra:-.1,rs:.9,rhs:"B" },
    ]
  },
  namaste: {
    desc: "Both palms pressed together at chest, slight bow",
    handshape: "flat", loc: "chest", motion: "press together",
    src: "ISL Common",
    frames: [
      { lx:-.08,ly:.05,la:.2, ls:.7,lhs:"flat", rx:.08,ry:.05,ra:-.2,rs:.7,rhs:"flat" },
      { lx:-.06,ly:.02,la:.15,ls:.7,lhs:"flat", rx:.06,ry:.02,ra:-.15,rs:.7,rhs:"flat" },
    ]
  },
  pain: {
    desc: "Both index fingers pointing, tap together twice at pain location",
    handshape: "D/index", loc: "body area", motion: "tap together",
    src: "ISL Medical",
    frames: [
      { lx:-.12,ly:.1,la:.3, ls:.05,lhs:"index", rx:.12,ry:.1,ra:-.3, rs:.05,rhs:"index" },
      { lx:-.06,ly:.08,la:.2,ls:.05,lhs:"index", rx:.06,ry:.08,ra:-.2,rs:.05,rhs:"index" },
      { lx:-.12,ly:.1,la:.3, ls:.05,lhs:"index", rx:.12,ry:.1,ra:-.3, rs:.05,rhs:"index" },
    ]
  },
  fever: {
    desc: "Index finger touches forehead, then moves down to chest",
    handshape: "D", loc: "forehead→chest", motion: "downward stroke",
    src: "ISL Medical",
    frames: [
      { rx:.05,ry:-.35,ra:0,rs:.05,rhs:"index" },
      { rx:.05,ry:.0,  ra:0,rs:.05,rhs:"index" },
      { rx:.05,ry:.15, ra:0,rs:.05,rhs:"index" },
    ]
  },
  medicine: {
    desc: "Middle finger taps palm twice — tablet/pill sign in ISL",
    handshape: "middle-tap", loc: "palm", motion: "double tap",
    src: "ISL Medical",
    frames: [
      { lx:-.15,ly:.1,la:.1,ls:.7,lhs:"palm", rx:.1,ry:.05,ra:.1,rs:.1,rhs:"mid" },
      { lx:-.15,ly:.08,la:.1,ls:.7,lhs:"palm", rx:.1,ry:.08,ra:.05,rs:.1,rhs:"mid" },
      { lx:-.15,ly:.1,la:.1,ls:.7,lhs:"palm", rx:.1,ry:.05,ra:.1,rs:.1,rhs:"mid" },
    ]
  },
  stomach: {
    desc: "Circular rub on stomach area with flat B-hand",
    handshape: "B-flat", loc: "stomach", motion: "circular rub",
    src: "ISL Medical",
    frames: [
      { lx:.0,  ly:.15,la:.1, ls:.6,lhs:"flat" },
      { lx:.05, ly:.12,la:.15,ls:.6,lhs:"flat" },
      { lx:-.05,ly:.18,la:.05,ls:.6,lhs:"flat" },
    ]
  },
  how: {
    desc: "Both curved C-hands face up, twist outward",
    handshape: "C", loc: "chest level", motion: "twist outward",
    src: "ISL Grammar",
    frames: [
      { lx:-.16,ly:.05,la:.3, ls:.5,lhs:"C", rx:.16,ry:.05,ra:-.3, rs:.5,rhs:"C" },
      { lx:-.2, ly:.03,la:.5, ls:.6,lhs:"C", rx:.2, ry:.03,ra:-.5, rs:.6,rhs:"C" },
    ]
  },
  yes: {
    desc: "A-hand (fist) nods up and down at chin level",
    handshape: "A-fist", loc: "chin", motion: "nod up-down",
    src: "ISL Basic",
    frames: [
      { rx:.04,ry:-.05,ra:0,rs:.0,rhs:"A" },
      { rx:.04,ry:.05, ra:0,rs:.0,rhs:"A" },
      { rx:.04,ry:-.05,ra:0,rs:.0,rhs:"A" },
    ]
  },
  no: {
    desc: "Index + middle fingers extend, snap closed on thumb twice",
    handshape: "index+mid snap", loc: "chin level", motion: "snap closed",
    src: "ISL Basic",
    frames: [
      { rx:.08,ry:-.02,ra:-.1,rs:.35,rhs:"no1" },
      { rx:.08,ry:-.02,ra:-.1,rs:.0, rhs:"A"   },
      { rx:.08,ry:-.02,ra:-.1,rs:.35,rhs:"no1" },
    ]
  },
  doctor: {
    desc: "D-hand taps inner wrist (pulse point) twice",
    handshape: "D", loc: "wrist/pulse", motion: "double tap",
    src: "ISL Profession",
    frames: [
      { lx:-.18,ly:.12,la:.1,ls:.7,lhs:"palm", rx:.05,ry:.08,ra:-.2,rs:.05,rhs:"D" },
      { lx:-.18,ly:.1, la:.1,ls:.7,lhs:"palm", rx:.05,ry:.1, ra:-.2,rs:.05,rhs:"D" },
      { lx:-.18,ly:.12,la:.1,ls:.7,lhs:"palm", rx:.05,ry:.08,ra:-.2,rs:.05,rhs:"D" },
    ]
  },
  please: {
    desc: "Flat B-hand circles on chest",
    handshape: "B-flat", loc: "chest", motion: "circle on chest",
    src: "ISL Polite",
    frames: [
      { rx:.04,ry:.0, ra:.1,rs:.7,rhs:"flat" },
      { rx:.08,ry:.04,ra:.3,rs:.7,rhs:"flat" },
      { rx:.0, ry:.06,ra:.5,rs:.7,rhs:"flat" },
    ]
  },
  water: {
    desc: "W-hand (3 fingers) taps chin twice",
    handshape: "W", loc: "chin", motion: "double tap chin",
    src: "ISL Basic",
    frames: [
      { rx:.02,ry:-.08,ra:0,rs:.4,rhs:"no1" },
      { rx:.02,ry:-.04,ra:0,rs:.4,rhs:"no1" },
      { rx:.02,ry:-.08,ra:0,rs:.4,rhs:"no1" },
    ]
  },
  eat: {
    desc: "Bunched fingers tap mouth twice (O-hand to mouth)",
    handshape: "O-bunch", loc: "mouth", motion: "tap to mouth",
    src: "ISL Basic",
    frames: [
      { rx:.0,ry:-.18,ra:0,rs:.0,rhs:"A" },
      { rx:.0,ry:-.12,ra:0,rs:.0,rhs:"A" },
      { rx:.0,ry:-.18,ra:0,rs:.0,rhs:"A" },
    ]
  },
  rest: {
    desc: "Neutral — arms relaxed at sides",
    handshape: "rest", loc: "sides", motion: "none",
    src: "ISL",
    frames: [
      { lx:-.02,ly:.25,la:.05,ls:.3,lhs:"rest", rx:.02,ry:.25,ra:-.05,rs:.3,rhs:"rest" },
    ]
  },
  default: {
    desc: "Fingerspell / approximate — word not in ISL database",
    handshape: "rest", loc: "—", motion: "neutral",
    src: "Fallback",
    frames: [
      { lx:-.02,ly:.25,la:.05,ls:.3,lhs:"rest", rx:.02,ry:.25,ra:-.05,rs:.3,rhs:"rest" },
    ]
  }
};
