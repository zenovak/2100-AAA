/**
 * A Standard constrained component with Padding-X meant as root of each sections
 * @param {*} className extends the current preconfigured className.\
 * `mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 ...`
 * @param {*} children the content 
 */
export const ContainerPX = ({className, children, ...props}) => {
    return (
        <div 
            {...props}
            className={"mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 " + className}>
            {children}
        </div>
    )
}


/**
 * A Standard constrained component with Padding-X meant as root of each sections.
 * Full width on Mobile, padded and constrained centered above.
 * @param {*} className extends the current preconfigured className.\
 * `mx-auto max-w-7xl sm:px-6 lg:px-8 ...`
 * @param {*} children the content 
 */
export const ContainerPX0 = ({className, children, ...props}) => {
    return (
        <div 
            {...props}
            className={"mx-auto max-w-7xl sm:px-6 lg:px-8 " + className}>
            {children}
        </div>
    );
}


/**
 * A standard container with only Padding-Y. Meant as the root container for any given sections.
 * @param {*} className extends the current preconfigured className.\
 * `py-24 sm:py-32 ...`
 * @param {*} children the content 
 */
export const ContainerPY = ({className, children, ...props}) => {
    return (
        <div
            {...props} 
            className={"py-24 sm:py-32 " + className}>
            {children}
        </div>
    );
}


/**
 * A Containert with Padding-Y, small. Meant as the root container for any given sections.
 * @param {*} className extends the current preconfigured className.\
 * `py-16` 
 * @param {*} children the content 
 */
export const ContainerPYsm = ( {className, children, ...props}) => {
    return (
        <div 
            {...props}
            className={"py-16 " + className}
        >
            {children}
        </div>
    );
}

/**
 * A Constrained Component with smaller max-width. Meant for setting inner contents such as\
 * accordion blocks, alert boxes, text groups, and more
 * @param {*} className extends the current preconfigured className.\
 * `max-w-3xl mx-auto ...`
 * @param {*} override option to override the currently preconfigured classNames. Defaults `false`
 * @param {*} children the content 
 */
export const ConstrainedContainer = ({ className, override, children, ...props }) => {
    return (
        <div
            {...props}
            className={override ? className : "max-w-3xl mx-auto " + className}
        >
            {children}
        </div>
    );
}