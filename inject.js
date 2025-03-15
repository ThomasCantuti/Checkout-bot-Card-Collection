const i = setInterval(() => {
    if (window.turnstile) {
      clearInterval(i);
  
      // Store the original render method
      const originalRender = window.turnstile.render;
  
      // Override the render method
      window.turnstile.render = (a, b) => {
        let p = {
          type: "TurnstileTaskProxyless",
          websiteKey: b.sitekey,
          websiteURL: window.location.href,
          data: b.cData,
          pagedata: b.chlPageData,
          action: b.action,
          userAgent: navigator.userAgent,
        };
  
        console.log(JSON.stringify(p));
  
        // Call the original render function with provided arguments
        const result = originalRender.call(window.turnstile, a, b);
  
        // Save the callback
        window.tsCallback = b.callback;
  
        // Return the result of the original render method
        return result;
      };
    }
  }, 1);