export const TextField = ({ className, override, children, ...props }) => {
  return (
    <div
      {...props}
      className={override ? className : className + ` flex items-center rounded-md bg-white w-full 
          outline-1 -outline-offset-1 outline-gray-300 
          has-[input:focus-within]:outline-2 has-[input:focus-within]:-outline-offset-2 has-[input:focus-within]:outline-indigo-600`}
    >
      {children}
    </div>
  )
}

TextField.Indicator = ({ className, override, children, ...props }) => {
  return (
    <div {...props} className={override ? className : className + " shrink-0 text-base text-gray-500 select-none sm:text-sm/6"}>
      {children}
    </div>
  )
}
TextField.Indicator.displayName = "TextField.Indicator";

TextField.Input = ({ id, name, type, register, registerProps, className, override, ...props }) => {
  return (
    <input
      id={id}
      name={name}
      type={type}
      {...register(name, registerProps)}
      className={override ? className : "block min-w-0 grow py-1.5 px-3 text-base text-gray-900 placeholder:text-gray-400 focus:outline-none sm:text-sm/6  " + className}
      {...props}
    />
  );
}
TextField.Input.displayName = "TextField.Input";