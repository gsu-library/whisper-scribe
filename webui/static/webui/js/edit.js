(() => {
   'use strict';
   const autoplay = document.querySelector('#autoplay');
   const mediaPlayer = document.querySelector('#media');
   const transcriptionId = window.location.pathname.split('/').pop();
   let transcriptionParts = document.querySelectorAll('.transcription-part');


   // Setup transcription part updates
   transcriptionParts.forEach(part => {
      part.addEventListener('change', async obj => {
         const data = {
            field: obj.target.dataset.field,
            value: obj.target.value
         };
         let result = await callApi('/api/transcriptions/' + transcriptionId, data, 'POST');
      });
   });


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

      // Enable tooltips
      const tooltipTriggerList = segment.querySelectorAll('[data-bs-toggle="tooltip"]');
      const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl, {trigger : 'hover'}));

      // Update input fields on change
      inputs.forEach(input => {
         input.addEventListener('change', async obj => {
            const data = {
               field: obj.target.dataset.field,
               value: obj.target.value
            };
            let result = await callApi('/api/segments/' + segmentId, data, 'POST');
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

      if(response.status == 200) {
         const json = await response.json();
         let segment = newSegment(json.id, json.start, json.end);
         segment = segment.childNodes[0];
         // TODO: should not have to select child node here

         if(where < 0) { clickedSegment.before(segment);  }
         else if( where > 0) { clickedSegment.after(segment); }
         setupSegment(segment);
      }
      else {
         // show some error
      }
   }


   // Function: deleteSegment
   async function deleteSegment(segmentId) {
      let segment;

      // segmentId should never be 0 due to autoincrement - if it ever is this will not work on segment 0
      if(segmentId && (segment = document.querySelector(`.segment[data-index='${segmentId}']`))) {
         const data = { method: 'DELETE' };
         let response = await callApi('/api/segments/' + segmentId, data, 'POST');

         if(response.status == 204) {
            segment.remove();
         }
         else {
            // placeholder
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


   // Function newSegment
   // Creates and returns segment code
   function newSegment(segmentId, start, end) {
      let segmentCode = `<div class="segment mb-5" data-index="${segmentId}">
         <div class="row mb-3">
            <div class="col-3">
               <div class="form-floating">
                  <input type="text" class="form-control border-0" id="speaker-${segmentId}" name="speaker-${segmentId}" value="" placeholder="" data-field="speaker" />
                  <label for="speaker-${segmentId}" >Speaker</label>
               </div>
            </div>

            <div class="col-2">
               <div class="form-floating">
                  <input type="text" class="form-control border-0" id="start-${segmentId}" name="start-${segmentId}" value="${start.toFixed(3)}" placeholder="" data-field="start" />
                  <label for="start-${segmentId}">Start</label>
               </div>
            </div>

            <div class="col-2">
               <div class="form-floating">
                  <input type="text" class="form-control border-0" id="end-${segmentId}" name="end-${segmentId}" value="${end.toFixed(3)}" placeholder="" data-field="end" />
                  <label for="end-${segmentId}">End</label>
               </div>
            </div>
         </div>

         <div class="row mb-3">
            <textarea class="form-control" id="text-${segmentId}" name="text-${segmentId}" data-field="text"></textarea>
         </div>

         <div>
            <div class="btn-group" role="group">
               <button type="button" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-title="Play" data-bs-placement="bottom" aria-label="Play" data-type="play"><i class="bi bi-play-fill"></i></button>
               <button type="button" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-title="Pause" data-bs-placement="bottom" aria-label="Pause" data-type="pause"><i class="bi bi-pause-fill"></i></button>
               <button type="button" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-title="Quick Rewind" data-bs-placement="bottom" aria-label="Quick Rewind" data-type="rewind"><i class="bi bi-arrow-counterclockwise"></i></button>
               <button type="button" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-title="Add Segment Before" data-bs-placement="bottom" aria-label="Add Segment Before" data-type="add-before"><i class="bi bi-arrow-bar-up"></i></button>
               <button type="button" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-title="Add Segment After" data-bs-placement="bottom" aria-label="Add Segment After" data-type="add-after"><i class="bi bi-arrow-bar-down"></i></button>
            </div>

            <div class="float-end" role="group">
               <button class="btn btn-outline-danger border-0 segment-delete" data-bs-title="Delete Segment" data-bs-placement="bottom" aria-label="Delete Segment" data-type="delete"><i class="bi bi-x-lg"></i></button>
            </div>
         </div>
      </div>`;

      let temp = document.createElement('div');
      temp.innerHTML = segmentCode;
      return temp;
   }
})();
