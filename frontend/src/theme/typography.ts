export const typography = {
  "display-mega": {
    fontSize: 80,
    fontWeight: "500" as const,
    lineHeight: 84,
    letterSpacing: -1.6,
  },
  "display-xl": {
    fontSize: 56,
    fontWeight: "500" as const,
    lineHeight: 62,
    letterSpacing: -1.12,
  },
  "display-lg": {
    fontSize: 36,
    fontWeight: "500" as const,
    lineHeight: 43,
    letterSpacing: -0.36,
  },
  "display-md": {
    fontSize: 26,
    fontWeight: "500" as const,
    lineHeight: 39,
    letterSpacing: 0.195,
  },
  "row-title": {
    fontSize: 20,
    fontWeight: "600" as const,
    lineHeight: 26,
    letterSpacing: -0.2,
  },
  "title-md": {
    fontSize: 18,
    fontWeight: "700" as const,
    lineHeight: 22,
    letterSpacing: 0,
  },
  "title-sm": {
    fontSize: 16,
    fontWeight: "500" as const,
    lineHeight: 22,
    letterSpacing: 0.08,
  },
  "body-md": {
    fontSize: 14,
    fontWeight: "400" as const,
    lineHeight: 21,
    letterSpacing: 0,
  },
  "body-sm": {
    fontSize: 13,
    fontWeight: "400" as const,
    lineHeight: 20,
    letterSpacing: 0,
  },
  "reader-body": {
    fontSize: 17,
    fontWeight: "400" as const,
    lineHeight: 29,
    letterSpacing: 0.1,
  },
  caption: {
    fontSize: 12,
    fontWeight: "400" as const,
    lineHeight: 17,
    letterSpacing: 0,
  },
  "caption-uppercase": {
    fontSize: 11,
    fontWeight: "600" as const,
    lineHeight: 15,
    letterSpacing: 1.1,
    textTransform: "uppercase" as const,
  },
  "badge-micro": {
    fontSize: 10,
    fontWeight: "700" as const,
    lineHeight: 10,
    letterSpacing: 0.8,
    textTransform: "uppercase" as const,
  },
  button: {
    fontSize: 14,
    fontWeight: "700" as const,
    lineHeight: 14,
    letterSpacing: 1.4,
    textTransform: "uppercase" as const,
  },
  "nav-link": {
    fontSize: 13,
    fontWeight: "600" as const,
    lineHeight: 18,
    letterSpacing: 0.65,
    textTransform: "uppercase" as const,
  },
  "number-display": {
    fontSize: 80,
    fontWeight: "700" as const,
    lineHeight: 80,
    letterSpacing: -1.6,
  },
};

export const spacing = {
  xxxs: 4,
  xxs: 8,
  xs: 16,
  sm: 24,
  md: 32,
  lg: 48,
  xl: 64,
  xxl: 96,
  super: 128,
};

export const rounded = {
  none: 0,
  xs: 2,
  sm: 4,
  md: 6,
  lg: 8,
  xl: 12,
  full: 9999,
};

export const motion = {
  duration: {
    instant: 100,
    fast: 200,
    normal: 300,
    slow: 500,
    reader: 250,
  },
  easing: {
    standard: "cubic-bezier(0.4, 0.0, 0.2, 1)",
    decelerate: "cubic-bezier(0.0, 0.0, 0.2, 1)",
    accelerate: "cubic-bezier(0.4, 0.0, 1, 1)",
    spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
  },
};