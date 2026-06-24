// Standalone Streamlit Component Library helper for Vanilla JS
(function() {
  var ComponentMessageType = {
    COMPONENT_READY: "streamlit:componentReady",
    SET_COMPONENT_VALUE: "streamlit:setComponentValue",
    SET_FRAME_HEIGHT: "streamlit:setFrameHeight"
  };

  var Streamlit = {
    API_VERSION: 1,
    RENDER_EVENT: "streamlit:render",
    events: new EventTarget(),
    registeredMessageListener: false,
    lastFrameHeight: undefined,

    setComponentReady: function() {
      if (!Streamlit.registeredMessageListener) {
        window.addEventListener("message", Streamlit.onMessageEvent);
        Streamlit.registeredMessageListener = true;
      }
      Streamlit.sendBackMsg(ComponentMessageType.COMPONENT_READY, {
        apiVersion: Streamlit.API_VERSION
      });
    },

    setFrameHeight: function(height) {
      if (height === undefined) {
        height = document.body.scrollHeight;
      }
      if (height === Streamlit.lastFrameHeight) {
        return;
      }
      Streamlit.lastFrameHeight = height;
      Streamlit.sendBackMsg(ComponentMessageType.SET_FRAME_HEIGHT, { height: height });
    },

    setComponentValue: function(value) {
      Streamlit.sendBackMsg(ComponentMessageType.SET_COMPONENT_VALUE, {
        value: value,
        dataType: "json"
      });
    },

    onMessageEvent: function(event) {
      var type = event.data["type"];
      if (type === Streamlit.RENDER_EVENT) {
        Streamlit.onRenderMessage(event.data);
      }
    },

    onRenderMessage: function(data) {
      var args = data["args"];
      if (args == null) {
        args = {};
      }
      var disabled = Boolean(data["disabled"]);
      var theme = data["theme"];
      if (theme) {
        var style = document.getElementById("streamlit-theme-style");
        if (!style) {
          style = document.createElement("style");
          style.id = "streamlit-theme-style";
          document.head.appendChild(style);
        }
        style.innerHTML = `
          :root {
            --primary-color: ${theme.primaryColor};
            --background-color: ${theme.backgroundColor};
            --secondary-background-color: ${theme.secondaryBackgroundColor};
            --text-color: ${theme.textColor};
            --font: ${theme.font};
          }
        `;
      }
      var eventData = { disabled: disabled, args: args, theme: theme };
      var customEvent = new CustomEvent(Streamlit.RENDER_EVENT, {
        detail: eventData
      });
      Streamlit.events.dispatchEvent(customEvent);
    },

    sendBackMsg: function(type, data) {
      window.parent.postMessage(Object.assign({ isStreamlitMessage: true, type: type }, data), "*");
    }
  };

  window.Streamlit = Streamlit;
})();
