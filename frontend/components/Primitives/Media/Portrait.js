import Image from "next/image";


/**
 * Portraits are Image components with predefined stylings and sizing behavior.\
 * Represents a standard 1:1 square image
 * @param {image} image src string for the image resource
 * @param {className} className extends the className property. Is applied to portrait root element
 */
export const Portrait1x1 = ({ image, className }) => {
  return (
    <div
      className={"w-full aspect-square rounded-lg overflow-hidden " + className}
    >
      <Image
        src={image || "/images/default/default.png"}
        alt="image"
        className="w-full h-full object-center object-cover"
        width="480"
        height="480"
      />
    </div>
  );
}

/**
 * Portrait with a predefined aspect ratio of 3x2 (landscape)
 * @param {*} image src string for the image resource  
 */
export const Portrait3x2 = ({ image, className }) => {
  return (
    <div
      className={"w-full aspect-[3/2] rounded-lg overflow-hidden " + className}
    >
      <Image
        src={image || "/images/default/default.png"}
        alt="image"
        className="w-full h-full object-cover object-center"
        width="900"
        height="600"
      />
    </div>
  )
}

/**
 * Portrait with a predefined aspect ratio of 5x2 (wide landscape)
 * @param {*} image src string for the image resource  
 */
export const Portrait5x2 = ({ image, className }) => {
  return (
    <div className={"w-full aspect-[5/2] rounded-lg overflow-hidden " + className}>
      <Image
        src={image || "/images/default/default.png"}
        alt="image"
        width={1000}
        height={400}
        className="w-full h-full object-center object-cover"
      />
    </div>
  );
}


export const Portrait16x9 = ({ image, className }) => {
  return (
    <div className={"w-full aspect-[16/9] rounded-lg overflow-hidden " + className}>
      <Image
        src={image || "/images/default/default.png"}
        alt="image"
        width={1920}
        height={1080}
        className="w-full h-full object-center object-cover"
      />
    </div>
  );
}

/**
 * Free Aspect Ratio version
 * @param {*} param0 
 * @returns 
 */
export const Portrait = ({ image, className }) => {
  return (
    <div className={"w-full h-full rounded-lg overflow-hidden " + className}>
      <Image
        src={image || "/images/default/default.png"}
        alt="image"
        width={1920}
        height={1080}
        className="w-full h-full object-center object-cover"
      />
    </div>
  );
}