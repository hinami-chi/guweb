new Vue({
    el: '#country-select',
    delimiters: ["<%", "%>"],
    data() {
      return {
        countries: {
          flags: window.flags,
        },
      };
    },
});