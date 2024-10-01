(() => {
   // TODO: use more data attributes?
   // TODO: check event listener objects
   'use strict';
   const autoplay = document.querySelector('#autoplay');
   const mediaPlayer = document.querySelector('#media');
   const transcriptionId = window.location.pathname.split('/').pop();
   let title = document.querySelector('input[name="title"]');

   // Title update
   title.addEventListener('change', obj => {
      let data = { value: obj.target.value };
      callApi('/api/transcriptions/' + transcriptionId, data, 'POST');
   });

   // Segment events
   let segments = document.querySelectorAll('.segment-part');
   segments.forEach(segment => {
      const field = segment.name.split('-')[0];
      const segmentId = segment.name.split('-')[1];

      // Play video on textarea click
      segment.addEventListener('focus', () => {
         if(segment.name.startsWith('text')) {
            let start = document.querySelector('#start-'+segmentId);
            let end = document.querySelector('#end-'+segmentId);

            if(autoplay.checked) {
               mediaPlayer.currentTime = start.value;
               mediaPlayer.play();
            }
         }
      });

      // Update field
      segment.addEventListener('change', async obj => {
         let data = {
            field: field,
            value: obj.target.value,
         };

         data = await callApi('/api/segments/' + segmentId, data, 'POST');
         console.log(data);
      });
   });

   // Segment deletes
   let deleteButtons = document.querySelectorAll('.segment-delete');
   deleteButtons.forEach(button => {
      button.addEventListener('click', async () => {
         const id = button.dataset.index;
         const data = { method: 'DELETE' };
         let response = await callApi('/api/segments/' + id, data, 'POST');
         console.log(`delete segment ${id} response: ${response.status}`);

         if(response.status == 204) {
            // Todo: fade out and/or display toast?
            button.closest('.segment').remove();
         }
         else {
            // TODO: display some error
         }
      });
   });


   // Function: callApi
   // Calls API to update a segment
   async function callApi(apiPath, data, method = 'GET') {
      let headers = {
         'Content-Type': 'application/json',
         'X-Requested-With': 'XMLHttpRequest',
      };

      if(method.toUpperCase() == 'POST') {
         headers['X-CSRFToken'] = document.querySelector('[name=csrfmiddlewaretoken]').value;
      }

      const response = await fetch(apiPath, {
         method: method.toUpperCase(),
         body: JSON.stringify(data),
         headers: headers,
         mode: 'same-origin',
      });

      // const responseData = await response.json();
      // return response.json();
      return response;
   }
})();
