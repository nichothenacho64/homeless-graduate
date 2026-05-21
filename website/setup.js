export function addFonts(layout) {
    const fontFamily = '"Source Sans 3", sans-serif';

    return {
        ...layout,
        font: {
            ...layout.font,
            family: fontFamily
        },
        hoverlabel: {
            ...layout.hoverlabel,
            font: {
                ...layout.hoverlabel?.font, // optional chaining is neeeded here to prevent accessing .font on undefined
                family: fontFamily
            }
        }
    }
}