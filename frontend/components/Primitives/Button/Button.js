import Link from "next/link";
import { forwardRef } from "react";



const ButtonExample = ({ className, onClick, children, ...props }) => {
  return (
    <button
      onClick={onClick}
      type="button"
      className="rounded-full border border-solid border-transparent transition-colors 
      flex items-center justify-center 
      bg-foreground text-background gap-2 
      hover:bg-[#383838] dark:hover:bg-[#ccc] 
      text-sm sm:text-base 
      h-10 sm:h-12 px-4 sm:px-5"
      {...props}>
      {children}
    </button>
  );
}


/**
 * Standard Themed buttons
 * @param {*} className this component's root className, is automatically appended to preconfigured style classes
 * @param {*} onClick
 * @param {*} href Optionally switches to a next/Link element if an href is provided
 * @param {*} size valid sizes are `xs | sm | md | lg | xl | 2xl`
 * @param {*} variant dictates the buttons' themes. Valid variants are 
 * `primary | secondary | soft | text | invert`
 * @param {*} children
 * @returns 
 */
export const Button = forwardRef(function MyButton({ className, onClick, href, size, variant, children, ...props }, ref) {
  let sizeClass;
  let themeClass;

  const Element = href? Link : "button";

  switch (size) {
    case "xs":
      sizeClass = "text-xs px-2 py-1";
      break;
    case "sm":
      sizeClass = "text-sm px-2.5 py-1.5";
      break;
    case "lg":
      sizeClass = "text-sm px-3 py-2";
      break;
    case "xl":
      sizeClass = "text-sm px-3.5 py-2.5";
      break;
    case "2xl":
      sizeClass = "text-sm sm:text-base py-3 px-4 sm:px-5";
      break;
    case "3xl":
      sizeClass = "text-base py-3 px-9";
      break;
    default:
      sizeClass = "text-sm px-2.5 py-1.5";
      break;
  }

  switch (variant) {
    case "secondary":
      themeClass = "shadow-sm bg-white text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50";
      break;
    case "soft":
      themeClass = "shadow-sm bg-indigo-50 text-indigo-600 hover:bg-indigo-100";
      break;
    case "text":
      themeClass = "text-gray-900 hover:bg-gray-50";
      break;
    case "invert":
      themeClass = "shadow-sm bg-white text-indigo-600 hover:bg-white focus-visible:outline-white";
      break;
    default:
      themeClass = "shadow-sm bg-indigo-600 text-white hover:bg-indigo-500 focus-visible:outline-indigo-600";
      break;
  }

  return (
    <Element
      // type="button"
      onClick={onClick}
      href={href}
      {...props}
      className={`${themeClass} ${sizeClass} focus-visible:outline-2 focus-visible:outline-offset-2 ` + className}
    >
      {children}
    </Element>
  );
});