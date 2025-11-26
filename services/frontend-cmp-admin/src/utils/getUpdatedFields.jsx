export const getUpdatedFields = (original, updated) => {
  const diff = {};

  const isObject = (obj) =>
    obj && typeof obj === "object" && !Array.isArray(obj);

  const computeDiff = (orig, upd) => {
    const result = {};
    Object.keys(upd).forEach((key) => {
      const origVal = orig?.[key];
      const updVal = upd[key];

      if (Array.isArray(updVal)) {
        if (
          !Array.isArray(origVal) ||
          JSON.stringify(origVal) !== JSON.stringify(updVal)
        ) {
          result[key] = updVal;
        }
      } else if (isObject(updVal)) {
        const nestedDiff = computeDiff(origVal || {}, updVal);
        if (Object.keys(nestedDiff).length > 0) {
          result[key] = nestedDiff;
        }
      } else {
        if (updVal !== origVal) {
          result[key] = updVal;
        }
      }
    });
    return result;
  };

  return computeDiff(original, updated);
};
