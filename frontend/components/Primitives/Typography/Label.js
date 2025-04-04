export const Label = ({className, children }) => {
  return (
    <p className={`text-base font-semibold leading-7 text-indigo-600 ${className}`}>
      {children}
    </p>
  )
}