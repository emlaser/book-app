//You can refactor the code to use async/await like this: ```javascript 
document.addEventListener("DOMContentLoaded", async function () {
  try {
    const response = await fetch("/get_messages"); const data = await response.json();
    if (data.success) {
      const chatContainer = document.querySelector(".messages");
      data.messages.forEach((msg) => {
        const roleDiv = document.createElement("div"); roleDiv.classList.add("message-role");
        if (msg.role === "user") {
          roleDiv.classList.add("user");
        }
        roleDiv.textContent = msg.role.charAt(0).toUpperCase() + msg.role.slice(1);
        chatContainer.appendChild(roleDiv);
        const messageDiv = document.createElement("div"); messageDiv.classList.add(msg.role === "user" ? "user-message" : "assistant-message");
        messageDiv.textContent = msg.content; chatContainer.appendChild(messageDiv);
      });
    }
  } catch (error) {
    console.error("Error fetching messages:", error);
  }
});
//``` This refactored code uses `async/await` syntax to make the code more concise and easier to read. The `async` keyword before the function declaration allows the use of `await` within the function, making it easier to handle promises and asynchronous operations.


//You can refactor the code using async/await as shown below: ```javascript // Define an async function to utilize async/await 
async function fetchData() {
  try {
    // Fetch data from "/get_ids" 
    const responseIds = await fetch("/get_ids"); const dataIds = await responseIds.json();
    // Log the data from "/get_ids" 
    console.log("Data: ", dataIds, "Assistant ID: ", dataIds.assistant_id, "Thread ID: ", dataIds.thread_id);
    // Fetch data from "/get_files" 
    const responseFiles = await fetch("/get_files"); const dataFiles = await responseFiles.json();
    // Call the function to populate files 
    populateFiles(dataFiles.assistant_files);
  } catch (error) { console.error("Error fetching data:", error); }
}
// Call the fetchData function when the DOM content is loaded document.addEventListener("DOMContentLoaded", fetchData);
//``` In this refactored code: - An `async` function `fetchData` is defined to use `async/await`. - The `fetch` calls are changed to use `await` for handling promises. - The response data is accessed using `await response.json()`. - The code is enclosed in a `try...catch` block to handle any errors that may occur during the fetching process. - The `fetchData` function is then called when the DOM content is loaded using `document.addEventListener("DOMContentLoaded", fetchData)`.

//Here is the refactored code using `async/await`: 
//```javascript 
document.querySelector("form").addEventListener("submit", async function (event) {
  event.preventDefault();
  const messageInput = document.querySelector('textarea[name="message"]');
  const message = messageInput.value.trim(); const chatContainer = document.querySelector(".messages");
  // Append the user's message to the chat container 
  if (message) {
    const roleDiv = document.createElement("div"); roleDiv.classList.add("message-role");
    roleDiv.classList.add("user");
    roleDiv.textContent = "User"; chatContainer.appendChild(roleDiv);
    const userMessageDiv = document.createElement("div"); userMessageDiv.classList.add("user-message"); userMessageDiv.textContent = message; chatContainer.appendChild(userMessageDiv);
  }
  // Clear the message input 
  messageInput.value = "";
  try {
    // Send the user's message to the server using asynchronous fetch 
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    });
    const data = await response.json();
    if (data.success) {
      const roleDiv = document.createElement("div"); roleDiv.classList.add("message-role");
      roleDiv.classList.add("assistant");
      roleDiv.textContent = "Assistant"; chatContainer.appendChild(roleDiv);
      // Remove the typing indicator 
      const typingIndicator = document.querySelector(".typing-indicator-container");
      if (typingIndicator) typingIndicator.remove();
      // Append the assistant's message to the chat container 
      const assistantMessageDiv = document.createElement("div");
      assistantMessageDiv.classList.add("assistant-message");
      assistantMessageDiv.textContent = data.message; chatContainer.appendChild(assistantMessageDiv);
      // Scroll to the bottom of the chat container 
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }
  catch (error) {
    console.error("Error:", error);
  }
  // Create a typing indicator container 
  const typingIndicatorContainer = document.createElement("div");
  typingIndicatorContainer.classList.add("typing-indicator-container");
  // Create a typing indicator 
  const typingIndicator = document.createElement("div");
  typingIndicator.classList.add("typing-indicator"); typingIndicator.textContent = "•••";
  // Append the typing indicator to its container 
  typingIndicatorContainer.appendChild(typingIndicator);
  // Append the typing indicator container to the chat container 
  chatContainer.appendChild(typingIndicatorContainer);
  // Scroll to the bottom of the chat container 
  chatContainer.scrollTop = chatContainer.scrollHeight;
});
//``` This refactored code uses `async/await` to improve readability and manage asynchronous calls within the event handler more effectively.