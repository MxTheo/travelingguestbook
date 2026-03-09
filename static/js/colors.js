window.MyColors = {
    getBootstrapColors: function() {
        const cssVar = (name, fallback = '') => {
            const v = getComputedStyle(document.documentElement).getPropertyValue(name);
            return (v && v.trim()) || fallback;
        };
        return {
            primary: cssVar('--bs-primary', 'rgba(54,162,235,0.95)'),
            danger: cssVar('--bs-danger', 'rgba(220,53,69,0.9)'),
            warning: cssVar('--bs-warning', 'rgba(255,193,7,0.95)'),
            success: cssVar('--bs-success', 'rgba(25,135,84,0.95)'),
            secondary: cssVar('--bs-secondary', 'rgba(108,117,125,0.9)'),
            dark: cssVar('--bs-dark', 'rgba(33,37,41,0.9)'),
        };
    },
};
