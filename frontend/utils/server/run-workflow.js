

const ENGINE_BASE_ENDPOINT = process.env.WORKFLOW_ENGINE_URL;

export async function runAgent({agent}, onSuccess, onError) {
  try {
    const res = await fetch(ENGINE_BASE_ENDPOINT + "/api/task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(agent)
    });

    if (!res.ok) {
      const error = new Error("Failed to start agent task");
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
    console.log(error);
    onError && onError(error);

    return error;
  }
}