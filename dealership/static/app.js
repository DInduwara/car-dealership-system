(function(){
	const API = {
		login: "/api/auth/login/",
		refresh: "/api/auth/refresh/",
		register: "/api/auth/register/",
		me: "/api/auth/me/",
		forgot: "/api/auth/password/forgot/",
		reset: "/api/auth/password/reset/",
		cars: "/api/cars/",
		bookings: "/api/bookings/",
		staff: "/api/staff/",
		sales: "/api/sales/",
	};

	let auth = (function(){
		const key = "dw.auth";
		function load(){ try { return JSON.parse(localStorage.getItem(key)||"null"); } catch(_) { return null; } }
		function save(data){ localStorage.setItem(key, JSON.stringify(data)); }
		function clear(){ localStorage.removeItem(key); }
		function token(){ return load()?.access || null; }
		function role(){ return load()?.user?.role || null; }
		return { load, save, clear, token, role };
	})();

	function headers(){
		const h = { "Content-Type": "application/json" };
		const t = auth.token(); if (t) h["Authorization"] = `Bearer ${t}`;
		return h;
	}
	async function apiGet(url){ const r = await fetch(url, { headers: headers() }); if(!r.ok) throw await r.json().catch(()=>({detail:r.statusText})); return r.json(); }
	async function apiPost(url, body){ const r = await fetch(url, { method:"POST", headers: headers(), body: JSON.stringify(body)}); if(!r.ok) throw await r.json().catch(()=>({detail:r.statusText})); return r.json(); }
	async function apiPatch(url, body){ const r = await fetch(url, { method:"PATCH", headers: headers(), body: JSON.stringify(body)}); if(!r.ok) throw await r.json().catch(()=>({detail:r.statusText})); return r.json(); }
	async function apiDelete(url){ const r = await fetch(url, { method:"DELETE", headers: headers() }); if(!r.ok) throw await r.json().catch(()=>({detail:r.statusText})); return true; }

	function toast(msg, type){
		const cont = document.getElementById("toast-container"); if(!cont) return;
		const div = document.createElement("div"); div.className = `toast ${type||""}`; div.role = "status"; div.textContent = msg;
		cont.appendChild(div); setTimeout(()=>div.remove(), 3500);
	}

	function setCookie(name, value, days){ const d = new Date(); d.setTime(d.getTime()+(days*24*60*60*1000)); document.cookie = `${name}=${encodeURIComponent(value)}; expires=${d.toUTCString()}; path=/`; }
	function delCookie(name){ document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`; }

	function setRoleNav(){
		const r = auth.role();
		document.querySelectorAll(".admin-nav").forEach(el=> el.hidden = r !== "ADMIN");
		document.querySelectorAll(".staff-nav").forEach(el=> el.hidden = r !== "SALES");
		const login = document.getElementById("nav-login"); const reg = document.getElementById("nav-register");
		const logout = document.getElementById("nav-logout");
		if(login) login.hidden = !!r; if(reg) reg.hidden = !!r; if(logout) logout.hidden = !r;
		logout?.addEventListener("click", ()=>{ auth.clear(); delCookie("dw_role"); setRoleNav(); location.href = "/"; });
	}
	setRoleNav();

	function qs(o){ return Object.fromEntries(new FormData(o).entries()); }
	function requireMatch(a,b){ if(a!==b) throw {confirm_password: "Passwords do not match"}; }
	function getQuery(name){ return new URL(location.href).searchParams.get(name); }

	// Auth flows
	const loginForm = document.getElementById("login-form");
	if(loginForm){
		loginForm.addEventListener("submit", async (e)=>{
			e.preventDefault();
			const data = qs(loginForm); const body = { username: data.email, password: data.password };
			try{
				const res = await apiPost(API.login, body);
				auth.save({ access: res.access, refresh: res.refresh, user: res.user || {} });
				setCookie("dw_role", res.user?.role||"", 7);
				setRoleNav();
				const role = auth.role();
				if(role === "ADMIN") location.href = "/admin/dashboard";
				else if(role === "SALES") location.href = "/staff/dashboard";
				else location.href = "/";
			}catch(err){ document.getElementById("login-errors").textContent = err.detail || "Login failed"; }
		});
	}
	const registerForm = document.getElementById("register-form");
	if(registerForm){
		registerForm.addEventListener("submit", async (e)=>{
			e.preventDefault();
			const data = qs(registerForm); try{ requireMatch(data.password, data.confirm_password); }catch(err){ document.getElementById("register-errors").textContent = err.confirm_password; return; }
			try{
				await apiPost(API.register, { full_name: data.full_name, email: data.email, phone: data.phone, password: data.password, accept_terms: !!data.accept_terms });
				document.getElementById("register-success").hidden = false; toast("Account created. Please log in.", "success");
			}catch(err){ document.getElementById("register-errors").textContent = (err.detail || JSON.stringify(err)); }
		});
	}
	const forgotForm = document.getElementById("forgot-form");
	if(forgotForm){
		forgotForm.addEventListener("submit", async (e)=>{ e.preventDefault(); const data = qs(forgotForm); try{ await apiPost(API.forgot, { email: data.email }); toast("If the email exists, a link was sent.", "success"); document.getElementById("forgot-status").textContent = "Check your inbox."; }catch(err){ toast("Error: "+(err.detail||""), "error"); }});
	}
	const resetForm = document.getElementById("reset-form");
	if(resetForm){
		document.getElementById("reset-token").value = getQuery("token")||"";
		resetForm.addEventListener("submit", async (e)=>{ e.preventDefault(); const data = qs(resetForm); try{ requireMatch(data.password, data.confirm_password); await apiPost(API.reset+`?token=${encodeURIComponent(data.token)}`, { password: data.password, confirm_password: data.confirm_password }); toast("Password reset.", "success"); location.href = "/auth/login"; }catch(err){ document.getElementById("reset-status").textContent = err.detail || JSON.stringify(err); }});
	}

	// Profile
	const profileForm = document.getElementById("profile-form");
	if(profileForm){
		(async ()=>{ try{ const me = await apiGet(API.me); profileForm.full_name.value = [me.first_name, me.last_name].filter(Boolean).join(" "); profileForm.email.value = me.email||""; profileForm.phone.value = me.phone||""; }catch(_){ /* not logged in */ } })();
		profileForm.addEventListener("submit", async (e)=>{
			e.preventDefault(); const data = qs(profileForm); const [first, ...rest] = data.full_name.split(" "); try{ await apiPatch(API.me, { first_name:first, last_name:rest.join(" "), phone:data.phone }); toast("Profile saved", "success"); }catch(err){ toast("Save failed", "error"); }
		});
	}

	// Cars list
	const carsList = document.getElementById("cars-list");
	const carsFilters = document.getElementById("cars-filters");
	const carsPagination = document.getElementById("cars-pagination");
	if(carsList && carsFilters){
		let lastPageData = null;
		async function loadCars(params){
			const url = new URL(API.cars, location.origin);
			Object.entries(params||{}).forEach(([k,v])=>{ if(v!==""&&v!=null) url.searchParams.set(k,v); });
			const data = await apiGet(url.pathname+url.search);
			lastPageData = data;
			const results = data.results || data || [];
			carsList.innerHTML = results.map(c=> `<article class="car-card" tabindex="0"><a href="/cars/${c.id}"><div class="thumb" aria-hidden="true">${(c.photos?.[0]?.s3_key||"")?`<img alt="" src="${imgUrl(c.photos[0].s3_key)}"/>`:'<div class="placeholder" aria-hidden="true"></div>'}</div><h3>${c.make} ${c.model} ${c.year}</h3><p>${fmtPrice(c)}</p></a></article>`).join("");
			renderPagination(data);
		}
		function imgUrl(key){ return `/media/${key}`; }
		function fmtPrice(c){ return `${c.currency||"USD"} ${Number((c.discount_price??c.base_price)).toLocaleString()}`; }
		function renderPagination(data){ if(!carsPagination) return; const prev = data.previous; const next = data.next; const count = data.count||0; const pageSize = 20; const currentPage = Number(new URL(data.next||data.previous||"?page=1", location.origin).searchParams.get("page")) || 1; const pages = Math.ceil(count/pageSize)||1; carsPagination.innerHTML = `<button ${prev?"":"disabled"} id="cars-prev">Prev</button> <span>Page ${currentPage} of ${pages}</span> <button ${next?"":"disabled"} id="cars-next">Next</button>`; document.getElementById("cars-prev")?.addEventListener("click", ()=>{ if(prev) navigate(prev); }); document.getElementById("cars-next")?.addEventListener("click", ()=>{ if(next) navigate(next); }); }
		function navigate(url){ const u = new URL(url, location.origin); const params = Object.fromEntries(u.searchParams.entries()); loadCars(params); }
		carsFilters.addEventListener("submit", (e)=>{ e.preventDefault(); loadCars(qs(carsFilters)); });
		document.getElementById("clear-filters").addEventListener("click", ()=>{ carsFilters.reset(); loadCars({}); });
		loadCars({ ordering: "-created_at" });
	}

	// Car detail + booking widget
	const carSpecs = document.getElementById("car-specs");
	const slotsGrid = document.getElementById("slots-grid");
	const confirmBtn = document.getElementById("confirm-booking");
	if(carSpecs && slotsGrid){
		const carId = location.pathname.split("/").pop();
		let selectedSlot = null; let selectedDate = null; let car = null;
		(async ()=>{ car = await apiGet(`${API.cars}${carId}/`); renderCar(car); })();
		function renderCar(c){
			document.getElementById("car-breadcrumb").textContent = `${c.make} ${c.model}`;
			document.getElementById("car-title").textContent = `${c.make} ${c.model} ${c.year}`;
			document.getElementById("car-price").textContent = `${c.currency} ${Number((c.discount_price??c.base_price)).toLocaleString()}`;
			carSpecs.innerHTML = `<ul>${["fuel_type","transmission","body_type","mileage"].map(k=>`<li><strong>${label(k)}:</strong> ${c[k]??"-"}</li>`).join("")}</ul>`;
		}
		function label(k){ return ({fuel_type:"Fuel", transmission:"Transmission", body_type:"Body", mileage:"Mileage"})[k]||k; }
		// audit drawer
		document.getElementById("audit-trail-btn")?.addEventListener("click", ()=>{ const d = document.getElementById("audit-drawer"); if(d) d.hidden = false; });
		document.getElementById("close-audit")?.addEventListener("click", ()=>{ const d = document.getElementById("audit-drawer"); if(d) d.hidden = true; });
		document.getElementById("book-date").addEventListener("change", async (e)=>{
			selectedDate = e.target.value; selectedSlot = null; confirmBtn.disabled = true;
			if(!selectedDate) return; const data = await apiGet(`${API.cars}${carId}/available-slots/?date=${selectedDate}`);
			renderSlots(data.slots||[]);
		});
		function renderSlots(slots){
			slotsGrid.innerHTML = slots.map(s=> `<button type="button" role="option" aria-selected="false" aria-label="${fmtHour(s.startAt)}" data-start="${s.startAt}" data-end="${s.endAt}">${fmtHour(s.startAt)}</button>`).join("");
			slotsGrid.querySelectorAll("button").forEach(btn=> btn.addEventListener("click", ()=>{ slotsGrid.querySelectorAll("button").forEach(b=>{b.classList.remove("active"); b.setAttribute("aria-selected","false");}); btn.classList.add("active"); btn.setAttribute("aria-selected","true"); selectedSlot = { startAt: btn.dataset.start, endAt: btn.dataset.end }; confirmBtn.disabled = false; }));
		}
		confirmBtn.addEventListener("click", async ()=>{
			if(!auth.token()){ document.getElementById("login-modal").hidden = false; return; }
			try{
				const res = await apiPost(API.bookings, { car: carId, start_at: selectedSlot.startAt });
				toast("Booking requested.", "success");
			}catch(err){ const modal=document.getElementById("error-modal"); document.getElementById("error-message").textContent = err.detail || "Conflict. Please choose another slot."; modal.hidden=false; document.getElementById("close-error").onclick = ()=> modal.hidden=true; }
		});
		document.getElementById("close-login-modal")?.addEventListener("click", ()=> document.getElementById("login-modal").hidden = true);
	}

	// Home page search autocomplete
	const searchInput = document.getElementById("search-input");
	const suggestions = document.getElementById("search-suggestions");
	if(searchInput && suggestions){
		let t=null; searchInput.addEventListener("input", ()=>{ clearTimeout(t); const q = searchInput.value.trim(); if(!q){ suggestions.innerHTML=""; return; } t=setTimeout(async ()=>{ const res = await apiGet(`${API.cars}?search=${encodeURIComponent(q)}&page=1`); const items = res.results||[]; suggestions.innerHTML = items.slice(0,8).map(c=>`<li role="option"><a href="/cars/${c.id}">${c.make} ${c.model} ${c.year}</a></li>`).join(""); }, 250); });
	}

	// Bookings page
	const bookingsListEl = document.getElementById("bookings-list");
	if(bookingsListEl){
		let mode = "list"; let itemsCache = [];
		const calTitle = document.getElementById("cal-title"); const calGrid = document.getElementById("calendar-grid"); const calMode = document.getElementById("cal-mode");
		let current = new Date(); current.setDate(1);
		document.getElementById("tab-list").addEventListener("click", ()=>{ mode="list"; toggle(); });
		document.getElementById("tab-calendar").addEventListener("click", ()=>{ mode="calendar"; toggle(); renderCalendar(); });
		document.getElementById("cal-prev").addEventListener("click", ()=>{ if(calMode.value==="month"){ current.setMonth(current.getMonth()-1); } else { current.setDate(current.getDate()-7); } renderCalendar(); });
		document.getElementById("cal-next").addEventListener("click", ()=>{ if(calMode.value==="month"){ current.setMonth(current.getMonth()+1); } else { current.setDate(current.getDate()+7); } renderCalendar(); });
		function toggle(){ document.getElementById("bookings-calendar").hidden = mode!=="calendar"; bookingsListEl.hidden = mode!=="list"; }
		async function load(){ try{ const r = await apiGet(`${API.bookings}me/`); const items = r.results||r; itemsCache = items; renderList(items); maybeReminder(items); }catch(_){ bookingsListEl.innerHTML = "<p>Please log in.</p>"; } }
		function renderList(items){ bookingsListEl.innerHTML = `<table class="table"><thead><tr><th>Car</th><th>When</th><th>Status</th><th></th></tr></thead><tbody>${items.map(b=>`<tr><td>${b.car}</td><td>${fmtDt(b.start_at)}</td><td>${b.status}</td><td>${actionBtns(b)}</td></tr>`).join("")}</tbody></table>`; attachActions(items); }
		function actionBtns(b){ const can = ["PENDING","APPROVED"].includes(b.status); return can?`<button data-id="${b.id}" data-act="reschedule">Reschedule</button><button data-id="${b.id}" data-act="cancel">Cancel</button>`:""; }
		function attachActions(items){ bookingsListEl.querySelectorAll("button[data-act]").forEach(btn=> btn.addEventListener("click", ()=>{ const id = btn.dataset.id; const act = btn.dataset.act; if(act==="cancel") cancelBooking(id); if(act==="reschedule") openReschedule(id); })); }
		async function cancelBooking(id){ try{ await apiPatch(`${API.bookings}${id}/cancel-mine/`, {}); toast("Booking cancelled", "success"); load(); }catch(err){ toast("Unable to cancel", "error"); } }
		let currentResId = null; const resModal = document.getElementById("booking-reschedule-modal");
		async function openReschedule(id){ currentResId = id; resModal.hidden = false; document.getElementById("res-date").value = new Date().toISOString().slice(0,10); await loadResSlots(); }
		async function loadResSlots(){ const date = document.getElementById("res-date").value; const booking = (await apiGet(`${API.bookings}${currentResId}/`)); const carId = booking.car; const data = await apiGet(`${API.cars}${carId}/available-slots/?date=${date}`); const cont = document.getElementById("res-slots"); cont.innerHTML = data.slots.map(s=>`<button type="button" data-start="${s.startAt}">${fmtHour(s.startAt)}</button>`).join(""); let picked=null; cont.querySelectorAll("button").forEach(b=> b.addEventListener("click", ()=>{ cont.querySelectorAll("button").forEach(x=>x.classList.remove("active")); b.classList.add("active"); picked=b.dataset.start; document.getElementById("res-confirm").disabled=false; })); document.getElementById("res-confirm").onclick = async ()=>{ try{ await apiPatch(`${API.bookings}${currentResId}/reschedule/`, { start_at: picked }); toast("Rescheduled", "success"); resModal.hidden=true; load(); }catch(err){ toast("Unable to reschedule", "error"); } }; document.getElementById("res-cancel").onclick = ()=>{ resModal.hidden=true; } }
		function renderCalendar(){ if(!calTitle||!calGrid) return; calGrid.innerHTML=""; if(calMode.value==="month"){ const year=current.getFullYear(); const month=current.getMonth(); const first=new Date(year,month,1); const last=new Date(year,month+1,0); calTitle.textContent = first.toLocaleString(undefined, {month:"long", year:"numeric"}); const startDay=first.getDay(); const days=last.getDate(); const cells=[]; for(let i=0;i<startDay;i++){ cells.push("<div></div>"); } for(let d=1; d<=days; d++){ const dateStr = new Date(year,month,d).toISOString().slice(0,10); const dayItems = itemsCache.filter(b=> (b.start_at||"").slice(0,10)===dateStr); cells.push(`<div class="cal-day"><div class="date">${d}</div><div class="events">${dayItems.map(b=>`<span class="badge ${b.status.toLowerCase()}">${new Date(b.start_at).toLocaleTimeString([], {hour:"2-digit"})}</span>`).join("")}</div></div>`); } calGrid.style.gridTemplateColumns = "repeat(7, 1fr)"; calGrid.innerHTML = cells.join(""); } else { const start = new Date(current); const cells=[]; calTitle.textContent = `Week of ${start.toLocaleDateString()}`; for(let i=0;i<7;i++){ const d=new Date(start); d.setDate(start.getDate()+i); const dateStr = d.toISOString().slice(0,10); const dayItems = itemsCache.filter(b=> (b.start_at||"").slice(0,10)===dateStr); cells.push(`<div class="cal-day"><div class="date">${d.toLocaleDateString(undefined,{weekday:"short", month:"short", day:"numeric"})}</div><div class="events">${dayItems.map(b=>`<span class="badge ${b.status.toLowerCase()}">${new Date(b.start_at).toLocaleTimeString([], {hour:"2-digit"})}</span>`).join("")}</div></div>`); } calGrid.style.gridTemplateColumns = "repeat(7, 1fr)"; calGrid.innerHTML = cells.join(""); }
		}
		function maybeReminder(items){ const soon = items.find(b=>{ const t = new Date(b.start_at).getTime() - Date.now(); return t>0 && t < 24*60*60*1000 && ["APPROVED","PENDING"].includes(b.status); }); if(soon) toast("Reminder: You have a test drive within 24h.", "info"); }
		load();
	}

	// Admin pages wiring
	const qa = document.querySelector(".admin-quick-actions");
	if(qa){ qa.querySelectorAll("[data-href]").forEach(b=> b.addEventListener("click", ()=> location.href = b.dataset.href)); document.addEventListener("keydown", (e)=>{ if(e.key.toLowerCase()==='a') location.href='/admin/cars/new'; if(e.key.toLowerCase()==='b') location.href='/admin/bookings'; if(e.key.toLowerCase()==='s') location.href='/admin/staff'; if(e.key.toLowerCase()==='r') location.href='/admin/sales'; }); }

	const carsTable = document.getElementById("cars-table");
	if(carsTable){
		(async()=>{
			const data = await apiGet(API.cars);
			const items = data.results||data; carsTable.innerHTML = `<thead><tr><th><input type="checkbox" id="sel-all"/></th><th>Car</th><th>Price</th><th>Status</th><th></th></tr></thead><tbody>${items.map(c=>`<tr><td><input type="checkbox" data-id="${c.id}"/></td><td>${c.make} ${c.model} ${c.year}</td><td>${c.currency} ${Number((c.discount_price??c.base_price)).toLocaleString()}</td><td>${c.status}</td><td><button data-id="${c.id}" data-act="delete">Delete</button></td></tr>`).join("")}</tbody>`;
			carsTable.querySelectorAll("button[data-act='delete']").forEach(btn=> btn.addEventListener("click", async ()=>{ if(!confirm("Delete car?")) return; try{ await apiDelete(`${API.cars}${btn.dataset.id}/`); toast("Deleted", "success"); location.reload(); }catch(err){ toast("Failed to delete", "error"); } }));
			const bulkBtn = document.getElementById("bulk-sold"); bulkBtn?.addEventListener("click", async ()=>{ const ids=[...carsTable.querySelectorAll("input[type=checkbox][data-id]:checked")].map(i=>i.dataset.id); for(const id of ids){ try{ await apiPatch(`${API.cars}${id}/`, { status: "SOLD" }); }catch(_){} } toast("Marked sold", "success"); location.reload(); });
			const exportBtn = document.getElementById("export-csv"); exportBtn?.addEventListener("click", ()=> exportCSV(items, "cars.csv", ["id","make","model","year","base_price","discount_price","status"]));
		})();
	}

	const carForm = document.getElementById("car-form");
	if(carForm){
		const selects = ["fuel_type","transmission","body_type","drive_type","status","location"]; const options = {
			fuel_type:["PETROL","DIESEL","HYBRID","ELECTRIC","CNG","LPG"],
			transmission:["MANUAL","AUTOMATIC","CVT","DUAL_CLUTCH"],
			body_type:["SEDAN","HATCHBACK","SUV","COUPE","CONVERTIBLE","WAGON","VAN","PICKUP","OTHER"],
			drive_type:["FWD","RWD","AWD","4WD"],
			status:["AVAILABLE","RESERVED","SOLD","REMOVED"],
			location:["SHOWROOM","WAREHOUSE"],
		}; selects.forEach(n=>{ const sel=carForm.querySelector(`[name=${n}]`); if(sel) sel.innerHTML = `<option value=""></option>`+options[n].map(v=>`<option>${v}</option>`).join(""); });
		const photos = document.getElementById("photos"); const previews = document.getElementById("photo-previews"); photos?.addEventListener("change", ()=>{ previews.innerHTML = ""; [...photos.files].forEach(file=>{ const img=document.createElement("img"); img.alt=""; img.src = URL.createObjectURL(file); img.width=120; previews.appendChild(img); }); });
		carForm.addEventListener("submit", async (e)=>{ e.preventDefault(); const data = qs(carForm); try{ const res = await apiPost(API.cars, data); toast("Car created", "success"); if(photos?.files?.length){ for(const file of photos.files){ await uploadPhoto(res.id, file); } } location.href = "/admin/cars"; }catch(err){ toast("Failed to save car", "error"); } });
		async function uploadPhoto(carId, file){ const fd = new FormData(); fd.append("s3_key", file.name); fd.append("alt_text", file.name); await fetch(`${API.cars}${carId}/photos/`, { method:"POST", headers: { Authorization: headers()["Authorization"] }, body: fd }); }
	}

	const staffForm = document.getElementById("staff-form");
	if(staffForm){ staffForm.addEventListener("submit", async (e)=>{ e.preventDefault(); const data = qs(staffForm); try{ await apiPost(API.staff, data); toast("Staff created", "success"); location.href = "/admin/staff"; }catch(err){ toast("Failed to create staff", "error"); } }); }

	const staffTable = document.getElementById("staff-table");
	if(staffTable){ (async()=>{ const items = (await apiGet(API.staff)).results||[]; staffTable.innerHTML = `<thead><tr><th>User</th><th>Salary</th><th>Commission</th><th>Active</th><th></th></tr></thead><tbody>${items.map(s=>`<tr><td>${s.user}</td><td>${s.salary}</td><td>${s.commission_rate}%</td><td>${s.is_active?"Yes":"No"}</td><td><button data-id="${s.id}" data-act="metrics">Metrics</button></td></tr>`).join("")}</tbody>`; const drawer = document.getElementById("staff-metrics-drawer"); staffTable.querySelectorAll("button[data-act='metrics']").forEach(b=> b.addEventListener("click", async ()=>{ const m = await apiGet(`${API.staff}${b.dataset.id}/metrics/`); drawer.hidden=false; drawer.innerHTML = `<h3>Metrics</h3><p>Total Sales: ${m.total_sales_count}</p><p>Total Revenue: ${m.total_revenue}</p><button id='close-drawer'>Close</button>`; drawer.querySelector('#close-drawer').onclick=()=>drawer.hidden=true; })); })(); }

	const bookingsTable = document.getElementById("bookings-table");
	if(bookingsTable){ (async()=>{ const items = (await apiGet(API.bookings)).results||[]; bookingsTable.innerHTML = `<thead><tr><th>ID</th><th>Car</th><th>Customer</th><th>Start</th><th>Status</th><th></th></tr></thead><tbody>${items.map(b=>`<tr><td>${b.id}</td><td>${b.car}</td><td>${b.customer}</td><td>${fmtDt(b.start_at)}</td><td>${b.status}</td><td>${adminActions(b)}</td></tr>`).join("")}</tbody>`; bookingsTable.querySelectorAll("button[data-act]").forEach(btn=> btn.addEventListener("click", ()=> action(btn.dataset.act, btn.dataset.id))); function adminActions(b){ if(["PENDING","APPROVED"].includes(b.status)) return `<button data-id="${b.id}" data-act="approve">Approve</button><button data-id="${b.id}" data-act="decline">Decline</button><button data-id="${b.id}" data-act="complete">Complete</button><button data-id="${b.id}" data-act="noshow">No-Show</button>`; return ""; } async function action(act, id){ const map={approve:"approve",decline:"decline",complete:"complete",noshow:"no-show"}; try{ await apiPatch(`${API.bookings}${id}/${map[act]}/`, {}); toast("Updated", "success"); location.reload(); }catch(_){ toast("Failed", "error"); } } document.getElementById("export-bookings")?.addEventListener("click", ()=> exportCSV(items, "bookings.csv", ["id","car","customer","start_at","status"])); })(); }

	const salesTable = document.getElementById("sales-table");
	if(salesTable){ (async()=>{ const items = (await apiGet(API.sales)).results||[]; salesTable.innerHTML = `<thead><tr><th>ID</th><th>Car</th><th>Customer</th><th>Salesperson</th><th>Price</th><th>Method</th><th>Date</th></tr></thead><tbody>${items.map(s=>`<tr><td>${s.id}</td><td>${s.car}</td><td>${s.customer}</td><td>${s.salesperson}</td><td>${s.currency} ${s.sale_price}</td><td>${s.payment_method}</td><td>${fmtDt(s.sale_datetime)}</td></tr>`).join("")}</tbody>`; document.getElementById("export-sales")?.addEventListener("click", ()=> exportCSV(items, "sales.csv", ["id","car","customer","salesperson","sale_price","currency","payment_method","sale_datetime"])); })(); }

	function exportCSV(items, filename, cols){ const rows = [cols.join(",")].concat(items.map(it=> cols.map(c=> JSON.stringify(it[c]??"")).join(","))); const blob = new Blob([rows.join("\n")], {type:"text/csv"}); const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = filename; a.click(); }
	function fmtDt(s){ try{ return new Date(s).toLocaleString(); }catch(_){ return s; } }
	function fmtHour(s){ const d = new Date(s); return d.toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"}); }

	// Basic SEO/meta placeholders
	if(document.title === "DriveWise"){ const h1 = document.querySelector("main h1"); if(h1) document.title = `DriveWise — ${h1.textContent}`; }

	// Admin dashboard data
	if(document.getElementById("metric-total-cars")){
		(async()=>{
			try{
				const cars = await apiGet(API.cars);
				document.getElementById("metric-total-cars").textContent = (cars.count ?? (cars.results?.length||0));
				const bookings = await apiGet(API.bookings);
				document.getElementById("metric-pending-bookings").textContent = (bookings.results||bookings||[]).filter(b=>b.status==="PENDING").length;
				const sales = await apiGet(API.sales);
				document.getElementById("metric-sales-month").textContent = (sales.results||sales||[]).length;
				const recent = (bookings.results||bookings||[]).slice(0,5);
				document.getElementById("recent-bookings").innerHTML = `<thead><tr><th>ID</th><th>Car</th><th>When</th><th>Status</th></tr></thead><tbody>${recent.map(b=>`<tr><td>${b.id}</td><td>${b.car}</td><td>${fmtDt(b.start_at)}</td><td>${b.status}</td></tr>`).join("")}</tbody>`;
				const top = (await apiGet(API.staff)).results||[]; document.getElementById("top-staff").innerHTML = top.slice(0,4).map(s=>`<div class="card"><h4>${s.user}</h4><p>Sales: ${s.total_sales_count??"-"}</p></div>`).join("");
			}catch(_){ /* ignore */ }
		})();
	}
})();