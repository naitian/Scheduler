

Note to self (feel free to read this even if you're not me though...):

`building_abbreviations.json` was generated with a Javascript snippet in Dev Tools:

```js
const building_map = {}
document.querySelectorAll(".field-item p").forEach(val => {
	let [abbr, full, campus] = val.innerText.split(/\n\s/);
	building_map[abbr] = {
		'name': full,
		campus
	};
})
copy(building_map);
```
