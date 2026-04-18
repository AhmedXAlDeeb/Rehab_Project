import { createTheme } from "@mui/material/styles";
import type { CSSProperties } from "react";

declare module "@mui/material/styles" {
  interface TypographyVariants {
    mono: CSSProperties;
  }

  interface TypographyVariantsOptions {
    mono?: CSSProperties;
  }
}

declare module "@mui/material/Typography" {
  interface TypographyPropsVariantOverrides {
    mono: true;
  }
}

export const appTheme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#0f766e",
      contrastText: "#f9fffd",
    },
    secondary: {
      main: "#b45309",
      contrastText: "#fffaf2",
    },
    background: {
      default: "#f3f1ea",
      paper: "#fffdf7",
    },
    text: {
      primary: "#1f2937",
      secondary: "#4b5563",
    },
    divider: "rgba(15, 23, 42, 0.12)",
  },
  shape: {
    borderRadius: 14,
  },
  typography: {
    fontFamily: '"Space Grotesk", "Segoe UI", sans-serif',
    h3: {
      fontWeight: 700,
      letterSpacing: "-0.02em",
    },
    h5: {
      fontWeight: 700,
      letterSpacing: "-0.01em",
    },
    body2: {
      lineHeight: 1.55,
    },
    mono: {
      fontFamily: '"IBM Plex Mono", "Consolas", monospace',
      fontSize: "0.82rem",
    },
  },
  components: {
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});
