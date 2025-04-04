function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}


/**
 * Use to get nested objects via string operation\
 * `https://stackoverflow.com/questions/6491463/accessing-nested-javascript-objects-and-arrays-by-string-path`
 * @param {*} obj DataObject
 * @param {*} propString property in string path
 * @returns 
 */
export function getObjectPropByString(obj, propString) {
  const result = propString.split('.').reduce((p, c) => p && p[c] || null, obj);
  return result;
}


/**
 * This is StoneIndex's implementation of an automatic table. Given a dataArray, and an Array of property names,
 * the table automatically plots itself
 * @param {fields} fields list of fields supported by this table \
 * `["name", "address", ...]`
 * @param {dataArray} dataArray array of data for this table. 
 * @param {canEdit} canEdit bool. Render an edit button?
 * @param {onEdit} onEdit callback when an entry's edit button is clicked\
 * `onEdit(item, index)` where item represents the item from dataArray and its index accordingly
 * @returns `
 */
export const TableExample = ({ fields, dataArray, canEdit, onEdit }) => {
  return (
    <table className="min-w-full border-separate border-spacing-0 ">
      <thead>
        <tr>
          {fields.map((item, index) => (
            index == 0 ? // first item style
              <th
                key={item}
                scope="col"
                className="sticky top-0 z-10 border-b border-gray-300 bg-white bg-opacity-75 py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 backdrop-blur backdrop-filter sm:pl-6 lg:pl-8"
              >
                {item}
              </th>
              : // other items
              <th
                key={item}
                scope="col"
                className="sticky top-0 z-10 border-b border-gray-300 bg-white bg-opacity-75 px-3 py-3.5 text-left text-sm font-semibold text-gray-900 backdrop-blur backdrop-filter"
              >
                {item}
              </th>
          ))}
          {canEdit &&
            <th
              scope="col"
              className="sticky top-0 z-10 border-b border-gray-300 bg-white bg-opacity-75 py-3.5 pl-3 pr-4 backdrop-blur backdrop-filter sm:pr-6 lg:pr-8"
            >
              <span className="sr-only">Edit</span>
            </th>}
        </tr>
      </thead>
      <tbody>
        {dataArray && dataArray.map((item, index) => (
          // for each entry...
          <tr key={index}>
            {fields.map((field, fieldIndex) => (
              // asign a column
              fieldIndex == 0 ?
                <td
                  key={field}
                  className={classNames(
                    index !== item.length - 1 ? 'border-b border-gray-200' : '',
                    'whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6 lg:pl-8'
                  )}
                >
                  {getObjectPropByString(item, field)}
                </td>
                :
                <td
                  key={field}
                  className={classNames(
                    index !== item.length - 1 ? 'border-b border-gray-200' : '',
                    'whitespace-nowrap px-3 py-4 text-sm text-gray-500 sm:table-cell'
                  )}
                >
                  {getObjectPropByString(item, field)}
                </td>
            ))}
            {canEdit &&
              <td
                className={classNames(
                  index !== item.length - 1 ? 'border-b border-gray-200' : '',
                  'relative whitespace-nowrap py-4 pr-4 pl-3 text-right text-sm font-medium sm:pr-8 lg:pr-8'
                )}
              >
                <button
                  onClick={
                    () => {
                      onEdit &&
                        onEdit(item, index)
                    }
                  }
                  className="text-indigo-600 hover:text-indigo-900" >

                  Edit<span className="sr-only"></span>
                </button>
              </td>}
          </tr>
        ))}
      </tbody>
    </table>
  );
}







const people = [
  { name: 'Lindsay Walton', title: 'Front-end Developer', email: 'lindsay.walton@example.com', role: 'Member' },
  // More people...
]

export const TableExampleFullWidth = () => {
  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-base font-semibold leading-6 text-gray-900">Users</h1>
          <p className="mt-2 text-sm text-gray-700">
            A list of all the users in your account including their name, title, email and role.
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            type="button"
            className="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Add user
          </button>
        </div>
      </div>
      <div className="mt-8 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle">
            <table className="min-w-full divide-y divide-gray-300">
              <thead>
                <tr>
                  <th
                    scope="col"
                    className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6 lg:pl-8"
                  >
                    Name
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Title
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Email
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Role
                  </th>
                  <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6 lg:pr-8">
                    <span className="sr-only">Edit</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {people.map((person) => (
                  <tr key={person.email}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6 lg:pl-8">
                      {person.name}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{person.title}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{person.email}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{person.role}</td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6 lg:pr-8">
                      <a href="#" className="text-indigo-600 hover:text-indigo-900">
                        Edit<span className="sr-only">, {person.name}</span>
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
