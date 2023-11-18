import reactRecommended from "eslint-plugin-react/configs/recommended.js";
import globals from "globals";

export default [
  {
    files: ["**/*.{js,mjs,cjs,jsx,mjsx,ts,tsx,mtsx}"],
    ...reactRecommended,
  },
];
