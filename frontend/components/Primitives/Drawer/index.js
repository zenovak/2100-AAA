import { Fragment, useRef } from 'react';
import { Dialog, DialogBackdrop, DialogTitle, Transition, TransitionChild } from '@headlessui/react';
import { Icon } from '@iconify/react';


/**
 * An Improved version of Drawer with animations. The Drawer's children represents its contents.
 * 
 * @param {open} open open state reference
 * @param {onClose} onClose `void () => {}` callback when the drawer is closed by the user either by tapping outside the panel or via the close btn
 * @param {anchor} anchor position of the drawer. Valid Values are:
 * ```
 * left | right | bottom
 * ```
 * @param {title} title Label for the drawer. Can be left empty
 * @param {children} children the contents of this drawer
 * @returns 
 * 
 * @example
 * ```jsx
 * export default function example() {
 *    const [open, setOpen] = useState(false);
 *    return (
 *    <div>
 *      <button onClick={()=>setOpen(true)}>Open drawer</button>
 *      <Drawer2 
 *        anchor="left"
 *        open={open}
 *        onClose={()=>setOpen(false)}
 *      />
 *    </div>
 *    );
 * }
 * ```
 */
export const Drawer = ({ open, onClose, anchor, title, children }) => {

  const focusRef = useRef(null);

  let positionStyle = undefined;
  let widthStyle = undefined;
  let animation = undefined;

  switch (anchor) {
    case "left": {
      positionStyle = "inset-y-0 left-0 sm:pr-10";
      widthStyle = "w-screen max-w-md";
      animation = "-translate-x-full";
      break;
    }

    case "bottom": {
      positionStyle = "inset-x-0 bottom-0 pt-10";
      widthStyle = "w-full";
      animation = "translate-y-full";
      break;
    }

    default: {
      positionStyle = "inset-y-0 right-0 sm:pl-10";
      widthStyle = "w-screen max-w-md";
      animation = "translate-x-full";
      break;
    }
  }

  return (
    <Transition
      className="z-30"
      show={open}
      as={Fragment}>
      <Dialog
        initialFocus={focusRef}
        as="div"
        className="fixed inset-0 overflow-hidden"
        onClose={onClose}>
        <div className="absolute inset-0 overflow-hidden">
          <TransitionChild
            as={Fragment}
            enter="ease-in-out duration-500"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in-out duration-500"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="absolute inset-0 bg-gray-800 bg-opacity-75 transition-opacity" />
          </TransitionChild>

          {/* postion style */}
          <div className={"pointer-events-none fixed flex max-w-full " + positionStyle}>
            <TransitionChild
              as={Fragment}
              enter="transform transition ease-in-out duration-500 sm:duration-700"
              enterFrom={animation}
              enterTo="translate-x-0"
              leave="transform transition ease-in-out duration-500 sm:duration-700"
              leaveFrom="translate-x-0"
              leaveTo={animation}
            >
              {/* Panel */}
              <div
                className={"pointer-events-auto " + widthStyle}>
                <div className="flex h-full flex-col bg-white py-6 shadow-xl">
                  <div className="px-4 sm:px-6">
                    <div className="flex items-start justify-between">
                      <DialogTitle className="text-lg font-medium text-gray-900">
                        {title}
                      </DialogTitle>
                      <div className="ml-3 flex h-7 items-center">
                        <button
                          type="button"
                          className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2"
                          onClick={onClose}
                        >
                          <span className="sr-only">Close panel</span>
                          <Icon icon="mdi:close" className="h-6 w-6" aria-hidden="true" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div
                    ref={focusRef}
                    className="relative mt-6 h-full px-4 sm:px-6">
                    {children ||
                      <div className="h-full w-full px-4 sm:px-6">
                        <div className="h-full border-2 border-dashed border-gray-200" aria-hidden="true" />
                      </div>
                    }
                  </div>
                </div>
              </div>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}