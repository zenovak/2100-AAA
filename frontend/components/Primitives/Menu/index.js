import { Menu as BaseMenu, MenuButton, MenuItem, MenuItems, Transition } from "@headlessui/react";
import { Fragment } from "react";


export const Menu = ({ className, override, children, ...props }) => {
  return (
    <BaseMenu 
      as="div" 
      className={override? className: "relative inline-block text-left " + className} {...props}>
      {children}
    </BaseMenu>
  );
}

Menu.Button = ({ as, className, children, ...props }) => {
  return (
    <MenuButton
      as={as}
      className={className}
      {...props}
    >
      {children}
    </MenuButton>
  );
}
Menu.Button.displayName = "Menu.Button";

Menu.Panel = ({ anchor, className, override, children, ...props }) => {
  let anchorClass;

  switch (anchor) {
    case "lt":
      anchorClass = "-translate-x-full -left-2 top-0";
      break;
    case "lc":
      anchorClass = "top-1/2 -translate-y-1/2 -left-2 -translate-x-full";
      break;
    case "rb":
      anchorClass = "-right-2 translate-x-full bottom-0 ";
      break;

    case "rt":
      anchorClass = "translate-x-full -right-2 top-0";
      break;
    case "rc":
      anchorClass = "top-1/2 -translate-y-1/2 -right-2 translate-x-full";
      break;
    case "lb":
      anchorClass = "bottom-0 -translate-x-full -left-2";
      break;

    case "tl":
      anchorClass = "-top-2 -translate-y-full left-0";
      break;
    case "tr":
      anchorClass = "-top-2 -translate-y-full right-0";
      break;
    case "tc":
      anchorClass = "bottom-full left-1/2 -translate-x-1/2 mb-4";
      break;

    case "br":
      // alternative style
      // anchorClass = "right-0 origin-top-right mt-2";
      anchorClass = "right-0 -bottom-2 translate-y-full";
      break;
    case "bc":
      anchorClass = "-bottom-2 translate-y-full left-1/2 -translate-x-1/2";
      break;
    // defaults bottom, left
    default:
      // alternative style
      // anchorClass = "left-0 origin-top-left mt-2";
      anchorClass = "left-0 -bottom-2 translate-y-full";
      break;
  }

  return (
    <Transition
      as={Fragment}
      enter="transition ease-out duration-100"
      enterFrom="transform opacity-0 scale-95"
      enterTo="transform opacity-100 scale-100"
      leave="transition ease-in duration-75"
      leaveFrom="transform opacity-100 scale-100"
      leaveTo="transform opacity-0 scale-95"
    >
      <MenuItems
        {...props}
        className={override? className: `absolute ${anchorClass} divide-y divide-gray-100 rounded-md bg-white shadow-lg ring-1 ring-black/5 focus:outline-none ` + className}>
        {/* Create new div style for groups */}
        {children}
      </MenuItems>
    </Transition>
  );
}
Menu.Panel.displayName = "Menu.Panel";

Menu.Item = ({ as, className, children, ...props }) => {
  return (
    <MenuItem
      as={as}
      {...props}
      className={className}
    >
      {children}
    </MenuItem>
  );
}
Menu.Item.displayName = "Menu.Item";