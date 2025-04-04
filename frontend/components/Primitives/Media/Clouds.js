import Image from "next/image";


/**
 * Adds a centered array of logos
 * @param {*} images  `[{src, alt}]` an array of logo images
 * @param {*} className appends to the root container className 
 * @returns 
 */
export const Clouds = ({ images=[], className }) => {
  return (
    <div className={"flex justify-center lg:justify-around items-center flex-wrap flex-shrink gap-x-8 gap-y-10 " + className}>
        {images.map((item, index) => (
          <Image 
            key={index}
            alt={item.alt || "logo"}
            src={item.src}
            width={158}
            height={48}
            className="max-h-12 object-contain"
          />
        ))}
    </div>
  );
}