import classNames from 'classnames';

export const Instructions = () => (
  <div>
    <h2 className={classNames('color-black', 'pl-3')}>Instructions</h2>
    <ul className={classNames('color-black', 'mb-3')}>
      <li>
        Click <b>Upload File</b> to upload a file, it will be stored in an S3 bucket that the File Transfer App can pull from
      </li>
      <li>
        <b>Select a file</b> from the drop down you want to transfer to one or more devices
      </li>
      <li>
        Check the box to <b>select all the devices</b> you want to transfer the file to
      </li>
      <li>
        If you want to schedule the Task in the future <b>select a Start Time</b>, this will default to NOW if not selected
      </li>
      <li>
        Click <b>Transfer</b> to create a Task and start transferring the selected file to the selected devices
      </li>
      <li>
        Clicking <b>Transfer</b> again will create a new Task for any selected device not in Transferring status
      </li>
      <li>
        Clicking <b>Cancel</b> in the Task table will terminate all Transferring tasks that are selected, all devices in the task will be Canceled
      </li>
    </ul>
  </div>
);
