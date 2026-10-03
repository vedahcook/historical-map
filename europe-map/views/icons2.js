// event icons: thin line drawings on a 16 x 16 grid (stroke only), shown without frames
const ICON = {
  war: '<path d="M2.5 2.5L10.6 10.6M13.5 2.5L5.4 10.6M8.6 12.6L12.6 8.6M3.4 8.6L7.4 12.6M10.6 10.6L12.6 12.6M5.4 10.6L3.4 12.6"/><circle cx="13.3" cy="13.3" r="1"/><circle cx="2.7" cy="13.3" r="1"/>',
  revolt: '<path d="M4.6 7.4V4.4a1.05 1.05 0 0 1 2.1 0v3M6.7 7.2V3.5a1.05 1.05 0 0 1 2.1 0v3.7M8.8 7.2V3.8a1.05 1.05 0 0 1 2.1 0v3.4M10.9 7.2V5a1.05 1.05 0 0 1 2.1 0v4.4c0 2-1.5 3.4-3.4 3.4H7.4c-2 0-3.4-1.4-3.4-3.4V8.6c0-.7.5-1.2 1.2-1.2h3.2a1.05 1.05 0 0 1 0 2.1H6.6M5.6 12.8v2.4M11.2 12.8v2.4"/>',
  politics: '<path d="M10.6 9.6V5.2L7.6 2.2H3.6v11.6h4.6M7.6 2.2v3h3M5.6 7.4h3M5.6 9.8h2"/><circle cx="11.6" cy="12.2" r="2.4"/><path d="M10.6 14.4l-.6 1.4M12.6 14.4l.6 1.4"/>',
  fire: '<path d="M8 14.8c-2.8 0-4.6-1.9-4.6-4.5 0-2.8 2.1-4 2.7-7.4 1.6 1 2.5 2.6 2.5 4.1.7-.6 1.2-1.6 1.2-2.7 1.8 1.4 3 3.5 3 6 0 2.6-1.9 4.5-4.8 4.5zM8 14.8c-1.2 0-2-.9-2-2.1 0-1.4 1.2-2 1.5-3.4 1.4.9 2.5 2 2.5 3.4 0 1.2-.8 2.1-2 2.1z"/>',
  quake: '<path d="M2.2 7.6L8 2.8l5.8 4.8M3.6 6.6v7.8h8.8V6.6M8.8 4.4L6.8 8l2.4 1.6-1.8 4.8"/>',
  epidemic: '<circle cx="8" cy="8" r="3.6"/><path d="M8 4.4V2.6M8 11.6v1.8M4.4 8H2.6M11.6 8h1.8M5.45 5.45L4.2 4.2M10.55 10.55l1.25 1.25M10.55 5.45L11.8 4.2M5.45 10.55L4.2 11.8"/><circle cx="8" cy="1.7" r=".9"/><circle cx="8" cy="14.3" r=".9"/><circle cx="1.7" cy="8" r=".9"/><circle cx="14.3" cy="8" r=".9"/><circle cx="3.55" cy="3.55" r=".9"/><circle cx="12.45" cy="12.45" r=".9"/><circle cx="12.45" cy="3.55" r=".9"/><circle cx="3.55" cy="12.45" r=".9"/>',
  building: '<path d="M1.8 5.6L8 2.2l6.2 3.4zM2.6 7.4h10.8M3.8 7.4v5.4M6.6 7.4v5.4M9.4 7.4v5.4M12.2 7.4v5.4M2 14.2h12M2.6 12.8h10.8"/>',
  learning: '<path d="M8 2.6L15 6 8 9.4 1 6zM4 7.9v3.2c0 1.1 1.8 2.1 4 2.1s4-1 4-2.1V7.9M13.4 6.6v4.6"/><circle cx="13.4" cy="11.9" r=".8"/>',
  faith: '<path d="M8 .9v4.2M6.2 2.5h3.6M3.6 8.7L8 5.1l4.4 3.6M4.4 8v7h7.2V8M6.6 15v-2.6a1.4 1.4 0 0 1 2.8 0V15"/>',
};
const KIND = { war: 'War, siege or massacre', revolt: 'Revolt or revolution', politics: 'Treaty, charter or change of rule', fire: 'Fire', quake: 'Earthquake or collapse', epidemic: 'Epidemic', building: 'Building', learning: 'University or school', faith: 'Church' };
