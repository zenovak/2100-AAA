import { DialogPanel, DialogTitle as ModalTitle, Dialog as Modal, Transition, TransitionChild, DialogBackdrop as ModalOverlay } from "@headlessui/react";
import { Fragment } from "react";


/**
 * Standard primitive dialog box. Appears in the center.
 * Aligns mid when called upon
 * @param {open} open
 * @param {onClose} onClose 
 * @param {initialFocus} initialFocus accepts a ref to target focus onto an element in this dialog
 * @param {className} className applies to the dialog panel
 * @param {override} override. Boolean whether to override or append the className
 * @param {children} children. children of this primitive
 */
export const Dialog = ({ open, onClose, initialFocus, className, override, children, ...props }) => {
  return (
    <Transition appear show={open} as={Fragment}>
      <Modal as="div" initialFocus={initialFocus} className="relative z-50" onClose={onClose}>
        <TransitionChild
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-300"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <ModalOverlay className="fixed inset-0 bg-black/25 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div className="fixed inset-0 w-screen">
          {/* https://github.com/tailwindlabs/headlessui/issues/2320 
              dialog shifts to left when closing requiring the base element to have w-screen
            */}
          <div className="flex flex-col min-h-full items-center justify-center p-4 text-center">
            <TransitionChild
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-400"
              leaveFrom="opacity-100 "
              leaveTo="opacity-0 "
            >
              <DialogPanel
                {...props}
                className={override ? className : 
                  `w-full max-w-md transform rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all ${className}`}>
                {children}
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Modal>
    </Transition>
  );
}

/**
 * The Dialog's semantic title.
 * @param {*} className
 * @param {*} override 
 * @param {*} children
 * @returns 
 */
const DialogTitle = ({ className, override, children, ...props }) => {
  return (
    <ModalTitle
      as="h3"
      className={override ? className : `text-lg font-medium leading-6 text-gray-900 ${className}`}
      {...props}
    >
      {children}
    </ModalTitle>
  )
}
Dialog.Title = DialogTitle;