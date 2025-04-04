import { Icon } from "@iconify/react";


/**
 * An Experimental Container meant for Navbar uses
 * Breaks into groups of 3 children, where the center child is always 
 * aligned dead center.
 * 
 * left and right child aligns left and right accordiningly
 * 
 * Must hold 3 children
 */
const Navigation3xExample = ({ navigation = [] }) => {
  return (
    <nav
      className="flex items-center justify-between p-6 lg:px-8">
      <div className="flex lg:flex-1">
        <a href="#" className="-m-1.5 p-1.5">
          <span className="sr-only">Your Company</span>
          <img
            alt=""
            src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=600"
            className="h-8 w-auto"
          />
        </a>
      </div>
      <div className="flex lg:hidden">
        <button
          type="button"
          className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700"
        >
          <span className="sr-only">Open main menu</span>
          <Icon icon="material-symbols:menu-rounded"
            aria-hidden="true" className="size-6" />
        </button>
      </div>

      <div className="hidden lg:flex lg:gap-x-12">
        {navigation.map((item) => (
          <a key={item.name} href={item.href} className="text-sm/6 font-semibold text-gray-900">
            {item.name}
          </a>
        ))}
      </div>

      <div className="hidden lg:flex lg:flex-1 lg:justify-end">
        <a href="#" className="text-sm/6 font-semibold text-gray-900">
          Log in <span aria-hidden="true">&rarr;</span>
        </a>
      </div>
    </nav>
  )
}

/**
 * 
 * @param {*} className
 * @param {*} override
 * @param {*} children 
 * @returns 
 */
export const Nav3x = ({ className = "", override, children, ...props }) => {
  return (
    <nav {...props} className={override ? className :
      "flex items-center justify-between " + className}>
      {children}
    </nav>
  )
}


/**
 * 
 * @param {*} className
 * @param {*} override
 * @param {*} children 
 * @returns 
 */
const NavItemLeft = ({ className = "", override, children, ...props }) => {
  return (
    <div {...props} className={override ? className :
      "flex flex-1 " + className
    }>
      {children}
    </div>
  )
}


/**
 * 
 * @param {*} className
 * @param {*} override
 * @param {*} children 
 * @returns 
 */
const NavItemRight = ({ className = "", override, children, ...props }) => {
  return (
    <div {...props} className={override ? className :
      "flex flex-1 justify-end " + className
    }>
      {children}
    </div>
  );
}


/**
 * 
 * @param {*} className
 * @param {*} override
 * @param {*} children 
 * @returns 
 */
const NavItemCenter = ({ className = "", override, children, ...props }) => {
  return (
    <div {...props} className={override ? className :
      "flex " + className
    }>
      {children}
    </div>
  )
}

Nav3x.Left = NavItemLeft;
Nav3x.Right = NavItemRight;
Nav3x.Center = NavItemCenter;