import fs from "fs";
import path from "path";

export async function POST(req) {
  try {
    const body = await req.json();
    const { steps } = body;

    if (!steps) {
      return new Response(
        JSON.stringify({ message: "Bad Request: steps data is required" }),
        { status: 400 }
      );
    }

    const filePath = path.join(
      process.cwd(),
      "src",
      "components",
      "features",
      "getStarted",
      "getStartedjson",
      "get-content.json"
    );

    fs.writeFileSync(filePath, JSON.stringify(steps, null, 2));

    return new Response(
      JSON.stringify({ message: "Steps updated successfully", data: steps }),
      { status: 200 }
    );
  } catch (error) {
    console.error("Error updating steps:", error);
    return new Response(
      JSON.stringify({ message: "Error updating steps", error: error.message }),
      { status: 500 }
    );
  }
}
