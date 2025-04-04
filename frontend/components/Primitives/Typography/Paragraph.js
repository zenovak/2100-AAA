/**
 * 
 * @param {*} variant dictates the Paragraphs' themes. Valid variants are 
 * `primary | secondary `
 * @param {*} size valid sizes are `xs | sm | md | lg`
 * @param {*} className
 * @param {*} children
 */
export const Paragraph = ({ variant, size, className, children }) => {
  let variantClass;
  let sizeClass;

  switch (variant) {
    case "secondary":
      variantClass = "text-white";
      break;
  
    default:
      variantClass = "text-gray-600";
      break;
  }

  switch (size) {
    case "lg":
      sizeClass = "leading-8 text-xl";
      break;

    case "sm":
      sizeClass = "text-base";
      break;

    case "xs":
      sizeClass = "text-sm";
      break;
  
    default:
      sizeClass = "text-lg";
      break;
  }

  return (
    <p className={`${variantClass} ${sizeClass} ` + className}>
      {children}
    </p>
  )
}