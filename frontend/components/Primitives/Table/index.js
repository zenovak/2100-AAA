// 
/** 
 * The Following Component sets are Primitives for building complex tables. 
 * For Faster simple usecases, please consider using premade blocks instead 
 * at @components/Blocks/Table
 * 
 * Author: @zenovak
*/
//



/**
 * 
 * @param {*} param0 
 * @returns 
 */
export const Table = ({ className, override, children, ...props }) => {
  return (
    <table className={override ? className : "w-full caption-bottom text-sm " + className} {...props}>
      {children}
    </table>
  );
}

Table.Headers = ({ className, override, children, ...props }) => {
  return (
    <thead className={override ? className : "" + className} {...props}>
      <tr>
        {children}
      </tr>
    </thead>
  );
}
Table.Headers.displayName = "Table.Headers";

Table.Header = ({ className, override, children, ...props }) => {
  return (
    <th
      scope="col"
      className={override ? className :
        "px-3 py-3.5 text-left text-sm font-semibold text-gray-900 " + className}
      {...props}
    >
      {children}
    </th>
  )
}
Table.Header.displayName = "Table.Header";

Table.Body = ({ className, override, children, ...props }) => {
  return (
    <tbody
      className={override ? className :
        "divide-y divide-gray-200 bg-white " + className}
      {...props}
    >
      {children}
    </tbody>
  )
}
Table.Body.displayName = "Table.Body";

Table.Row = ({ className, override, children, ...props }) => {
  return (
    <tr
      className={override ? className : " " + className}
      {...props}
    >
      {children}
    </tr>
  )
}
Table.Row.displayName = "Table.Row";

Table.Cell = ({ className, override, children, ...props }) => {
  return (
    <td
      className={override ? className :
        "whitespace-nowrap px-3 py-4 text-sm text-gray-500 " + className}
      {...props}
    >
      {children}
    </td>
  )
}
Table.Cell.displayName = "Table.Cell";
