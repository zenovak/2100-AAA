

const ENGINE_BASE_ENDPOINT = process.env.WORKFLOW_ENGINE_URL;

export async function runAgent({agent}, onSuccess, onError) {
  try {
    const res = await fetch(ENGINE_BASE_ENDPOINT + "/api/v1/chatrooms", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(agent)
    });

    if (!res.ok) {
      const error = new Error("Failed to create chatroom");
      error.info = await res.json();
      error.status = res.status;
      throw error;
    }

    const data = await res.json();
    if (onSuccess) {
      onSuccess(data);
    }

    return data;
  } catch (error) {
    console.log("Failed to create chatroom", error);
    onError && onError(error);

    return error;
  }
}