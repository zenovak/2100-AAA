import { PrismaClient } from '@prisma/client';

/**
 * Prisma client singleton. Use this to get an istance of prisma.
 */
let prisma;
if (process.env.NODE_ENV === 'production') {
  prisma = new PrismaClient();
} else {
  if (!global.prisma) {
    global.prisma = new PrismaClient();
  }
  prisma = global.prisma;
}

export default prisma;



/**
 * Handles Prisma Error for different operation codes.
 * Returns a status code & message JSON object
 * @param {*} error error thrown by prisma operations
 * @returns JSON response model\
 * {status, message}
 */
export function handlePrismaError(error) {
    switch (error.code) {
        case 'P2002':
            // handling duplicate key errors
            return {status: 409, message: `Duplicate field value: ${error.meta.target}`};
        case 'P2014':
            // handling invalid id errorors
            return {status: 400, message:`Invalid ID: ${error.meta.target}`};
        case 'P2003':
            // handling invalid data errorors
            return {status: 400, message:`Invalid input data: ${error.meta.target}`};
        default:
            // handling all other errors
            return {status: 500, message:`Something went wrong: ${error.message}`};
        }
};

