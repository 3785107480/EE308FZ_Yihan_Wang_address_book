# Screenshot and Complete Video Guide

This guide produces actual evidence for the final address-book version. The latest
assignment requires screenshots and a complete running video, but it does not
specify a minimum screenshot count. Use fictional data. Generated UI screenshots
are useful for layout review; a complete student-recorded demonstration and public
video link still need to be supplied.

## Prepare

1. Start the application using the README. Record the version/commit being shown.
2. Use a dedicated demonstration database, not an address book containing private
   contacts. Keep this database for the persistence part of the recording.
3. Open Import Excel and download the blank template and fictional sample. Do not
   imply the application silently came with these records; import is user-initiated.
4. Prepare Excel, Numbers, or LibreOffice so you can open the actual exported XLSX.
5. Turn off private notifications and keep text readable. Use a continuous recording
   with deliberate pauses rather than a video made only from still images.

## Suggested screenshots

| File | What to show | What the caption establishes |
|---|---|---|
| 01-main-interface.png | Main page with fictional contacts and action buttons | Usable page and summary |
| 02-multiple-method-form.png | Same person with 2 phones, 2 emails and another type | Repeated methods in one contact |
| 03-contact-details.png | Saved labels and full method values | Actual saved information |
| 04-bookmarks.png | Selected Bookmarks navigation and saved stars | Convenient bookmark access |
| 05-export-in-excel.png | Real workbook open, one row per contact, column labels | Genuine Excel format and all information |
| 06-import-result.png | Export restored in an empty test book with counts | Import restores exported data |
| 07-duplicate-import.png | Repeat import with skipped count | No extra exact duplicates |
| 08-invalid-import.png | Named row/format error and unchanged total | File validation and atomic rejection |
| 09-after-restart.png | Same saved details after server restart | Persistence with same database |
| 10-mobile-layout.png | Narrow viewport with readable controls | Responsive page layout |
| 11-github-commits.png | Published main history with at least 3 commits | Real history and contributor count |
| 12-release-and-pr.png | Published version/tag and actual PR | Release and review delivery |
| 13-public-cloud.png | Public app with address bar, if deployed | Optional cloud bonus evidence |

Keep each screenshot caption close to its image. For export screenshots, scroll
horizontally or add another image if otherwise some repeated method columns would
be hidden. A screenshot named "after restart" is not by itself proof of a restart;
show the restart procedure in the video.

## Complete running video script

Suggested duration: approximately 5–8 minutes; this is guidance, not an assignment
duration requirement. Show the real application and workbook, not only code.

1. **Identify the application.** State "Yihan Wang Address Book, individual EE308FZ
   Extreme Programming assignment". Show the application URL and final version.
2. **Create a contact.** Add a fictional name, organization, job title and note.
   Add a Mobile phone with a `+` prefix, a Home phone such as `001234567890`, two
   email addresses, a social handle and an address or website. Save and open detail.
3. **Edit the contact.** Change a label or note and save; show the updated value.
4. **Show bookmarks.** Star the contact, open Bookmarks, unstar it and show it
   disappears from that filtered view, then bookmark it again. Show the counts.
5. **Search.** Search for a method value or organization, then demonstrate a no-match
   search. Clear the search and return to All contacts.
6. **Add/import a second person.** Ensure more than one contact exists so that the
   exported workbook demonstrates one row per person.
7. **Export and inspect.** Click Export Excel. Open the downloaded XLSX in a
   spreadsheet viewer. Show the Contacts sheet, names in separate rows, Bookmarked,
   Notes, and Phone 1/2 and Email 1/2 label/value columns. Show the leading zero.
8. **Restore through import.** In this fictional demonstration database, delete the
   shown contacts using the app so it is empty. Import the exported XLSX. Show
   imported counts, restored bookmark, labels, notes and multiple values. Do not
   delete an unrelated user's contacts on a shared public installation.
9. **Repeat import.** Select the same file again. Show zero newly imported exact
   duplicates and the skipped count. The contact total should remain unchanged.
10. **Invalid file.** In a copy of the workbook, remove a Name on a populated row
    or enter a formula, save as XLSX and import it. Show the error and unchanged
    contacts. The workbook must be genuinely saved; just renaming an extension
    is not a compatible workbook.
11. **Persistence.** Stop the local server and restart it with the same database,
    or restart the deployed service if you administer it. Reload and show the
    same contacts/bookmarks. Do not change to a new database file during this step.
12. **Narrow screen.** Resize the browser or use its responsive mode and show that
    the form, actions and saved details remain usable.
13. **Published delivery.** Show GitHub commit history, per-author counts, release
    and pull request. If cloud bonus is claimed, also show the public application
    from another network and keep its actual URL visible.

If the current public demo is shared, another evaluator can change its records.
Use a local isolated demo for the destructive round trip and demonstrate public
reachability separately. Explain this rather than claiming user isolation.

## Publish and check

- Upload the complete recording through a CSDN-supported video path or a public
  service accepted by the course. Embed it and include a text link as a fallback.
- Play the video from a logged-out/private browser. The teaching staff must not
  need access to a private personal drive.
- Confirm audio/captions and screen text are legible. Keep each required function
  visible for long enough to understand.
- Verify all screenshots still match the released interface and data format.
- Link the real repository, codestyle, release, PR and optional cloud application.
- Record actual counts and PSP values. Do not fill them using fabricated estimates
  presented as measurements.
