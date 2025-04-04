import Link from "next/link";


export const NavLink = ({href, className, children, ...props}) => {
    return (
        <Link href={href} className={"text-sm leading-6 text-gray-600 hover:text-gray-900 " + className} {...props}>
            {children}
        </Link>
    );
}