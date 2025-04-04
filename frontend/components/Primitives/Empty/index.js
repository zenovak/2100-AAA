import { Icon } from "@iconify/react";


/**
 * An Empty state to show the user theres no resources
 * @param {*} icon
 * @param {*} title
 * @param {*} onClick
 * @param {*} className
 * @returns 
 */
export const EmptyFrame = ({ icon, title, onClick, className }) => {
  const Element = onClick? "button": "div";

  return (
    <Element 
      onClick={onClick}
      className={"relative block w-full border-2 border-gray-300 border-dashed rounded-lg p-12 text-center hover:border-gray-400 " + className}>
      <div className="w-full h-full flex items-center justify-center flex-col">
        <Icon
          className="h-12 w-12 text-gray-400"
          icon={icon}
          aria-hidden="true"
        />
        <span className="mt-2 block text-sm font-medium text-gray-900">{title}</span>
      </div>
    </Element>
  );
}