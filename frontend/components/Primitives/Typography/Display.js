export const Display = ({ size, className, variant, children }) => {
  let variantClass;
  let sizeClass;

  switch (size) {
    case "sm":
      sizeClass = "text-3xl";
      break;
  
    default:
      sizeClass = "text-4xl sm:text-6xl";
      break;
  }

  switch (variant) {
    case "secondary": 
      variantClass = "text-white";
      break;

    default:
      variantClass = "text-gray-900 dark:text-gray-100";
      break;
  }


  return (
    <h1 className={`text-4xl sm:text-6xl tracking-tight font-bold ${variantClass} ` + className }>
      {children}
    </h1>
  );
}