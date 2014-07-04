-- NOTE: Do not use 'value' > 1 for non-stackable items.
-- NOTE: The 'key' field for addons is a bit mask ((male << 16) | female).

-- Constants
local TYPE_ITEM = 1
local TYPE_CONTAINER = 2
local TYPE_ADDON = 3
local TYPE_MOUNT = 4

local HIST_QUERY = 'INSERT INTO `shop_history` \
	(`id`, `name`, `type`, `key`, `value`, `price`, `ordered`, `delivered`, `character_id`, `account_id`) \
	VALUES(NULL, %s, %d, %d, %d, %d, %d, %d, %d, %d);'

-- Returns a player object by their GUID (if they're online), otherwise returns nil.
local getPlayer = function(guid)
	local players = Game.getPlayers()
	for _, player in pairs(players) do
		if player:getGuid() == guid then
			return player
		end
	end

	return nil
end

function onThink()
	-- Query the shop orders.
	local resultId = db.storeQuery('SELECT * FROM `shop_order`;')

	-- Check whether the query has succeeded.
	if not resultId then
		return true
	end

	-- Prepare the reusable variables.
	local id, name, type, key, value, price, ordered, character_id
	local success

	-- Loop through the orders.
	repeat
		-- Find the receiver.
		character_id = result.getDataInt(resultId, 'character_id')
		local player = getPlayer(character_id)
		if player then
			-- Set the success flag to false.
			success = false

			-- Load the row values.
			id = result.getDataInt(resultId, 'id')
			name = result.getDataString(resultId, 'name')
			type = result.getDataInt(resultId, 'type')
			key = result.getDataInt(resultId, 'key')
			value = result.getDataInt(resultId, 'value')
			price = result.getDataInt(resultId, 'price')
			ordered = result.getDataInt(resultId, 'ordered')

			-- Regular items.
			if type == TYPE_ITEM then
				local item = Item(doCreateItemEx(key, value))
				if item then
					if player:addItemEx(item) then
						success = true
					end
				end
			-- Container items.
			elseif type == TYPE_CONTAINER then
				local container = Container(doCreateItemEx(1988))
				if container then
					for i = 1, value do
						container:addItem(key)
					end

					if player:addItemEx(container) then
						success = true
					end
				end
			-- Outfit addons.
			elseif type == TYPE_ADDON then
				local male = bit.rshift(key, 16)
				local female = bit.band(key, 0xFFFF)

				player:addOutfitAddon(male, value)
				player:addOutfitAddon(female, value)

				success = true
			-- Mounts.
			elseif type == TYPE_MOUNT then
				player:addMount(key)
				success = true
			else
				print('[Warning] Unknown shop order type ('.. type ..').')
			end

			-- Check whether we successfully delivered the order.
			if success then
				-- Send a text message to the player.
				player:sendTextMessage(MESSAGE_INFO_DESCR, 'You have received the "'.. name ..'" order.')

				-- Add an order history row.
				db.query(HIST_QUERY:format(
					db.escapeString(name),
					type, key, value,
					price, ordered, os.time(),
					character_id, player:getAccountId()
				))

				-- Delete the order row.
				db.query('DELETE FROM `shop_order` WHERE `id` = '.. id ..' LIMIT 1;')
			else
				-- Send a text message to the player.
				player:sendTextMessage(MESSAGE_INFO_DESCR, 'Failed to deliver the "'.. name ..'" order. \
					Please make sure that you have enough capacity/room.')
			end
		end
	until not result.next(resultId)

	-- Free the result and return.
	result.free(resultId)
	return true
end
