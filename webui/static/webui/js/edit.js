(() => {
   // TODO: use more data attributes?
   // TODO: check event listener objects
   'use strict';
   // TODO: save autoplay to local storage and load it from there
   const autoplay = document.querySelector('#autoplay');
   const mediaPlayer = document.querySelector('#media');
   const transcriptionId = window.location.pathname.split('/').pop();
   let title = document.querySelector('input[name="title"]');

   // Title update
   title.addEventListener('change', obj => {
      const data = { value: obj.target.value };
      callApi('/api/transcriptions/' + transcriptionId, data, 'POST');
   });

   // todo: get rid of transcripion id as it is above

   // Setup all segment events
   let segments = document.querySelectorAll('.segment');
   segments.forEach(setupSegment);


   // Function: setupSegment
   // Adds events to segments
   function setupSegment(segment) {
      const segmentId = segment.dataset.index;
      let inputs = segment.querySelectorAll('input');
      let textareas =  segment.querySelectorAll('textarea');
      let buttons = segment.querySelectorAll('button');
      let startTime = document.querySelector('#start-' + segmentId);

      // Update input fields on change
      inputs.forEach(input => {
         input.addEventListener('change', async obj => {
            const data = {
               field: obj.target.dataset.field,
               value: obj.target.value
            };
            let result = await callApi('/api/segments/' + segmentId, data, 'POST');
            // TODO: show result
         });
      });

      // Update textarea on change and add autoplay
      textareas.forEach(textarea => {
         // Autoplay
         textarea.addEventListener('focus', obj => {
            if(autoplay.checked) {
               mediaPlayer.currentTime = startTime.value;
               mediaPlayer.play();
            }
         });

         // Update
         textarea.addEventListener('change', async obj => {
            const data = {
               field: obj.target.dataset.field,
               value: obj.target.value
            };
            let result = await callApi('/api/segments/' + segmentId, data, 'POST');
            // TODO: show result
         });
      });

      // Add listeners to all buttons
      buttons.forEach(button => {
         const buttonType = button.dataset.type;

         button.addEventListener('click', () => {
            switch (buttonType) {
               case 'play':
                  mediaPlayer.currentTime = startTime.value;
                  mediaPlayer.play();
                  break;
               case 'pause':
                  mediaPlayer.pause();
                  break;
               case 'rewind':
                  let currentTime = mediaPlayer.currentTime;
                  mediaPlayer.currentTime = currentTime - 1.0;
                  // TODO: check to see if negative time breaks any browsers
                  break;
               case 'add-before':
                  createSegment(segmentId, -1);
                  break;
               case 'add-after':
                  createSegment(segmentId, 1);
                  break;
               case 'delete':
                  deleteSegment(segmentId);
                  break;
               default:
                  console.log('you should never see this');
            }
         });

         // Segment deletes
         // let deleteButtons = document.querySelectorAll('.segment-delete');
         // deleteButtons.forEach(button => {
         //    button.addEventListener('click', async () => {
         //       const id = button.dataset.index;
         //       const data = { method: 'DELETE' };
         //       let response = await callApi('/api/segments/' + id, data, 'POST');
         //       console.log(`delete segment ${id} response: ${response.status}`);

         //       if(response.status == 204) {
         //          // Todo: fade out and/or display toast?
         //          button.closest('.segment').remove();
         //       }
         //       else {
         //          // TODO: display some error
         //       }
         //    });
         // });
      });
   }


   // Function: createSegment
   async function createSegment(segmentId, where) {
      let otherSegment;
      let otherId = -1;
      const clickedSegment = document.querySelector(`.segment[data-index='${segmentId}']`);

      if(where < 0) {
         otherSegment = clickedSegment.previousElementSibling;
      }
      else if(where > 0) {
         otherSegment = clickedSegment.nextElementSibling;
      }
      else {
         // TODO: display segment creation error
         console.log('segment creation failed');
         return;
      }

      if(otherSegment && otherSegment.classList.contains('segment')) {
         otherId = otherSegment.dataset.index;
      }

      const data = {
         segmentId: segmentId,
         otherId: otherId,
         where: where
      };

      let response = await callApi('/api/segments/', data, 'POST');
   }


   // Function: deleteSegment
   async function deleteSegment(segmentId) {
      let segment;

      // segmentId should never be 0 due to autoincrement - if it ever is this will not work on segment 0
      if(segmentId && (segment = document.querySelector(`.segment[data-index='${segmentId}']`))) {
         const data = { method: 'DELETE' };
         let response = await callApi('/api/segments/' + segmentId, data, 'POST');

         if(response.status == 204) {
            // Todo: fade out and/or display toast?
            segment.remove();
         }
         else {
            // TODO: display some error
         }
      }
   }


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
