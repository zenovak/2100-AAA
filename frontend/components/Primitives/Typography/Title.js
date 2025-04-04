export const Title = ({ size, className, children }) => {
    let sizingClass;

    switch (size) {
        case "xs":
            sizingClass = "text-sm font-semibold  text-gray-900";
            break;
    
        default:
            sizingClass = "text-lg font-semibold text-gray-900";
            break;
    }


    return (
        <h3 className={ `leading-6 ${sizingClass} ` + className}>
            {children}
        </h3>
    )
}