/**
 * 
 * @param {*} variant dictates the Headline' themes. Valid variants are 
 * `primary | secondary `
 * @param {*} className
 * @param {*} children
 */
export const Headline = ({variant, className, children}) => {
    let variantClass;
    
    switch (variant) {
        case "secondary":
            variantClass = "text-white ";
            break;
    
        default:
            variantClass = "text-gray-950 ";
            break;
    }

    return (
        <h2 className={"text-3xl sm:text-4xl font-extrabold tracking-tight " + 
            variantClass + 
            className}>
            {children}
        </h2>
    );
}