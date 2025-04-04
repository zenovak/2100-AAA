import { MdiPerson } from "@/components/Icons/Material/Avatar";
import Image from "next/image";


/**
 * A standard Avatar icon for displaying people.\
 * Sets at default w-10
 * @param {*} image string of image resource 
 * @param {*} alt image alt text. Optional
 * @param {*} size string of \
 * `| xs, sm, md, lg, xl, 2xl |` defaults `md`\
 * `|  6,  8, 10, 12, 14,  16 |` in tailwind units
 * @param {*} className optional appending of CSS classes
 * @param {*} override bool. Overides the default CSS classes instead of append
 * @param {*} disableOptimization whether to use NextJS/Image. Default false.\
 * @param {*} disableRounded. Disables the default rounded-full tailwindCSS for the avatar
 * @returns 
 */
export const Avatar = ({ image, alt, size, className, override, disableOptimization, disableRounded, ...props }) => {
  let sizing;
  switch (size) {

    case "2xl":
      sizing = "w-16 h-16";
      break;

    case "xl":
      sizing = "w-14 h-14";
      break;

    case "lg":
      sizing = "w-12 h-12";
      break;

    case "sm":
      sizing = "w-8 h-8";
      break;

    case "xs":
      sizing = "w-6 h-6";
      break;

    default:
      sizing = "w-10 h-10";
      break;
  }
  const ImageElement = disableOptimization ? "img" : Image;

  if (!image) {
    return (
      <MdiPerson
        className={override ? className : `${disableRounded ? "" : "rounded-full"} object-cover ${sizing} ${className}`}
      />
    )
  }

  return (
    <ImageElement
      {...props}
      alt={alt || "avatar"}
      src={image || "/images/default/avatar.jpg"}
      width="300"
      height="300"
      className={override ? className : `${disableRounded ? "" : "rounded-full"} object-cover ${sizing} ${className}`}
    />
  );
}


/**
 * A stack of avatars
 * @param {size} size string of \
 * `| xs, sm, md, lg, xl |` defaults `md`
 * @param {dataArray} dataArray `[{image}, ...`]
 */
export const AvatarStack = ({ dataArray, size }) => {
  return (
    <div className="flex -space-x-2 overflow-hidden">
      {dataArray.map((item, index) => (
        <Avatar
          key={index}
          image={item.image}
          size={size}
          className="ring-2 ring-white"
        />
      ))}
    </div>
  );
}