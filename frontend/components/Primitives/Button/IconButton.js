import Link from "next/link";
import { forwardRef } from "react";

/**
 * Circular button with a single icon. No texts
 * @param {*} icon Icon element
 * @param {*} onClick 
 * @param {*} href
 * @param {*} alt Alternative text to describe this Button/Link
 * @param {*} size Dictates the size of the icon button. Valid sizes are:
 * `sm | md | lg`
 * @param {*} variant dictates the buttons' themes. Valid variants are 
 * `primary | secondary | soft | text | invert`
 * @param {*} className this component's root className, is automatically appended to preconfigured style classes
 */
export const IconButton = forwardRef(function myButton({ icon, onClick, href, alt, size, variant, className, ...props }, ref) {
  const Element = href ? Link : "button";
  let elementSizeClass;
  let iconSizeClass;
  let themeClass;

  iconSizeClass = "h-5 w-5";

  switch (size) {
    case "sm":
      elementSizeClass = "p-1";
      break;
    case "lg":
      elementSizeClass = "p-2";
      break;
    default:
      elementSizeClass = "p-1.5";
      break;
  }

  switch (variant) {
    case "secondary":
      themeClass = "shadow-sm bg-white text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50";
      break;
    case "soft":
      themeClass = "shadow-sm bg-indigo-50 text-indigo-600  hover:bg-indigo-100";
      break;
    case "text":
      themeClass = "text-gray-900 hover:bg-gray-50";
      break;
    case "invert":
      themeClass = "shadow-sm bg-white text-indigo-600 hover:bg-white focus-visible:outline-white";
      break;
    default:
      themeClass = "shadow-sm bg-indigo-600 hover:bg-indigo-500 focus-visible:outline-indigo-600 text-white";
      break;
  }

  // convert icon args into an "as" element
  const Icon = icon;

  return (
    <Element
      ref={ref}
      onClick={onClick}
      href={href}
      className={`rounded-full ${elementSizeClass} ${themeClass} focus-visible:outline-2 focus-visible:outline-offset-2 ${className}`}
      {...props}
    >
      <Icon className={iconSizeClass} aria-hidden="true" />
      <span className="sr-only">
        {alt}
      </span>
    </Element>
  );
});