
/**
 * Submits a API call to register the current user.
 * @param {*} username
 * @param {*} email
 * @param {*} password 
 * @param {*} onSuccess 
 * @param {*} onError 
 * @returns 
 */
export async function registerUser({ email, password }, onSuccess, onError) {
    try {
        const res = await fetch('/api/register', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: email,
                password: password,
            })
        });
    
        if (!res.ok) {
            const error = new Error("Failed to add user to chatroom");
            error.info = await res.json();
            error.status = res.status;
            throw error;
        }
    
        const data = await res.json();
        onSuccess && onSuccess(data);
    
        return data;
    } catch (error) {
        onError && onError(error);
        return error;
    }
}