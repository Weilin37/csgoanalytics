package main

import (
	"encoding/csv"
	//"fmt"
	"os"
	"strconv"
	"strings"

	dem "github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs"
	"github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs/common"
	"github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs/events"
)

type Output struct {
	Frame   int
	Events  interface{}
	Players [][]string
}

func main() {
	f, err := os.Open("C:\\Users\\Weilin\\Desktop\\dem2CSV\\demos\\natus-vincere-vs-vitality-m1-inferno.dem")
	defer f.Close()
	checkError(err)

	p := dem.NewParser(f)
	// Parameters
	// How many every frames to capture
	var CaptureRate = 10

	// Output variables
	var PlayerOutput []Output
	var SpottedOutput []Output
	var ShootOutput []Output
	var HurtOutput []Output


	// Register event handlers
	p.RegisterEventHandler(func(e events.WeaponFire) {
		if p.GameState().IsMatchStarted() == true {
			var shootData [][]string

			var WeaponFire = []string{
				strconv.Itoa(p.CurrentFrame()),
				e.Shooter.Name,
				strconv.FormatInt(int64(e.Weapon.Type), 10),
			}

			shootData = append(shootData, WeaponFire)
			oShoot := Output{
				Frame:   p.CurrentFrame(),
				Players: shootData,
			}
			ShootOutput = append(ShootOutput, oShoot)

			if p.CurrentFrame()%CaptureRate != 0 {
				var playersData [][]string
				for _, player := range p.GameState().Participants().Playing() {
					playersData = append(playersData, extractPlayerData(p.CurrentFrame(), player))
				}
				oPlayer := Output{
					Frame:   p.CurrentFrame(),
					Players: playersData,
				}
				PlayerOutput = append(PlayerOutput, oPlayer)
			}
		}
	})

	p.RegisterEventHandler(func(e events.PlayerHurt) {
		if p.GameState().IsMatchStarted() && e.Attacker != nil {
			var hurtData [][]string

			var WeaponFire = []string{
				strconv.Itoa(p.CurrentFrame()),
				e.Attacker.Name,
				e.Player.Name,
				strconv.FormatInt(int64(e.Health), 10),
				strconv.FormatInt(int64(e.Armor), 10),
				strconv.FormatInt(int64(e.Weapon.Type), 10),
				strconv.FormatInt(int64(e.HealthDamage), 10),
				strconv.FormatInt(int64(e.ArmorDamage), 10),
				strconv.FormatInt(int64(e.HitGroup), 10),
			}
			hurtData = append(hurtData, WeaponFire)
			oHurt := Output{
				Frame:   p.CurrentFrame(),
				Players: hurtData,
			}
			HurtOutput = append(HurtOutput, oHurt)

			if p.CurrentFrame()%CaptureRate != 0 {
				var playersData [][]string
				for _, player := range p.GameState().Participants().Playing() {
					playersData = append(playersData, extractPlayerData(p.CurrentFrame(), player))
				}
				oPlayer := Output{
					Frame:   p.CurrentFrame(),
					Players: playersData,
				}
				PlayerOutput = append(PlayerOutput, oPlayer)
			}
		}
	})

	// parse frame by frame
	for ok := true; ok; ok, err = p.ParseNextFrame() {
		checkError(err)

		gs := p.GameState()
		frame := p.CurrentFrame()

		var playersData [][]string
		var spottedData [][]string

		for _, player := range gs.Participants().Playing() {
			if gs.IsMatchStarted() == true && frame%CaptureRate == 0 {
				playersData = append(playersData, extractPlayerData(frame, player))
				var playersSpotted = gs.Participants().SpottersOf(player)
				if len(playersSpotted) > 0 {
					spottedData = append(spottedData, extractSpottedData(frame, player, playersSpotted))
				}
			}
		}

		oPlayer := Output{
			Frame:   frame,
			Players: playersData,
		}

		oSpotted := Output{
			Frame:   frame,
			Players: spottedData,
		}

		PlayerOutput = append(PlayerOutput, oPlayer)
		SpottedOutput = append(SpottedOutput, oSpotted)
	}

	err = csvExportPlayerData(PlayerOutput)
	checkError(err)

	err = csvExportSpottedData(SpottedOutput)
	checkError(err)

	err = csvExportShootData(ShootOutput)
	checkError(err)

	err = csvExportHurtData(HurtOutput)
	checkError(err)
}

// Event extraction
func extractSpottedData(frame int, player *common.Player, spottedPlayers []*common.Player) []string {
	var spottedPlayersStringArray []string
	for _, spottedPlayer := range spottedPlayers {
		spottedPlayersStringArray = append(spottedPlayersStringArray, spottedPlayer.Name)
	}

	return []string {
		strconv.Itoa(frame),
		player.Name,
		strings.Join(spottedPlayersStringArray, ", "),
	}
}

func extractPlayerData(frame int, player *common.Player) []string {
	var wepType string
	if wep := player.ActiveWeapon(); wep != nil {
		wepType = strconv.FormatInt(int64(wep.Type),10)
	} else {
		wepType = "Unknown"
	}

	return []string{
		strconv.Itoa(frame),
		player.Name,
		strconv.FormatUint(player.SteamID64,10),
		strconv.FormatFloat(player.Position().X, 'G', -1, 64),
		strconv.FormatFloat(player.Position().Y, 'G', -1, 64),
		strconv.FormatFloat(player.Position().Z, 'G', -1, 64),

		strconv.FormatFloat(player.Velocity().X, 'G', -1, 64),
		strconv.FormatFloat(player.Velocity().Y, 'G', -1, 64),
		strconv.FormatFloat(player.Velocity().Z, 'G', -1, 64),

		strconv.FormatFloat(float64(player.ViewDirectionX()), 'G', -1, 64),
		strconv.FormatFloat(float64(player.ViewDirectionY()), 'G', -1, 64),

		strconv.FormatInt(int64(player.Team),10),
		strconv.Itoa(player.Health()),
		strconv.Itoa(player.Armor()),
		strconv.Itoa(player.Money()),
		strconv.Itoa(player.EquipmentValueCurrent()),
		wepType,

		strconv.FormatFloat(float64(player.FlashDuration), 'G', -1, 64),

		strconv.FormatBool(player.IsAlive()),
		strconv.FormatBool(player.IsAirborne()),
		strconv.FormatBool(player.IsDucking()),
		strconv.FormatBool(player.IsScoped()),
		strconv.FormatBool(player.IsWalking()),
		strconv.FormatBool(player.IsInBombZone()),
		strconv.FormatBool(player.IsBlinded()),
		strconv.FormatBool(player.IsDefusing),
		strconv.FormatBool(player.IsPlanting),
		strconv.FormatBool(player.IsReloading),
		strconv.FormatBool(player.HasDefuseKit()),
		strconv.FormatBool(player.HasHelmet()),

		strconv.Itoa(player.Kills()),
		strconv.Itoa(player.Deaths()),
		strconv.Itoa(player.Assists()),
		strconv.Itoa(player.Score()),
		strconv.Itoa(player.MVPs()),
		strconv.Itoa(player.MoneySpentThisRound()),
	}
}


// CSV Export
func csvExportPlayerData(data []Output) error {
	file, err := os.OpenFile("resultPlayer.csv", os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0644)
	defer file.Close()
	if err != nil {
		return err
	}

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// header
	header := []string{
		"Frame", "Name", "SteamID", "Position_X", "Position_Y", "Position_Z",
		"Velocity_X", "Velocity_Y", "Velocity_Z", "ViewDirectionX", "ViewDirectionY",
		"Team", "Hp", "Armor", "Money", "CurrentEquipmentValue", "ActiveWeapon",
		"FlashDuration", "IsAlive", "IsAirborne", "IsDucking", "IsScoped", "IsWalking", "IsInBombZone", "IsBlinded", "IsDefusing", "IsPlanting", "IsReloading",
		"HasDefuseKit", "HasHelmet",
		"Kills", "Deaths", "Assists", "Score", "MVPs", "CashSpentThisRound",
	}
	if err := writer.Write(header); err != nil {
		return err // let's return errors if necessary, rather than having a one-size-fits-all error handler
	}

	// data
	for _, frameData := range data {
		for _, player := range frameData.Players {
			err := writer.Write(player)
			if err != nil {
				return err
			}
		}
	}

	return nil
}

func csvExportSpottedData(data []Output) error {
	file, err := os.OpenFile("resultSpotted.csv", os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0644)
	defer file.Close()
	if err != nil {
		return err
	}

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// header
	header := []string{
		"Frame", "PlayerSteamID", "PlayersSpotted",
	}
	if err := writer.Write(header); err != nil {
		return err // let's return errors if necessary, rather than having a one-size-fits-all error handler
	}

	// data
	for _, frameData := range data {
		for _, player := range frameData.Players {
			err := writer.Write(player)
			if err != nil {
				return err
			}
		}
	}

	return nil
}

func csvExportShootData(data []Output) error {
	file, err := os.OpenFile("resultShoot.csv", os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0644)
	defer file.Close()
	if err != nil {
		return err
	}

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// header
	header := []string{
		"Frame", "Shooter", "Weapon",
	}
	if err := writer.Write(header); err != nil {
		return err // let's return errors if necessary, rather than having a one-size-fits-all error handler
	}

	// data
	for _, frameData := range data {
		for _, player := range frameData.Players {
			err := writer.Write(player)
			if err != nil {
				return err
			}
		}
	}

	return nil
}

func csvExportHurtData(data []Output) error {
	file, err := os.OpenFile("resultHurt.csv", os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0644)
	defer file.Close()
	if err != nil {
		return err
	}

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// header
	header := []string{
		"Frame", "Shooter", "Victim", "VictimHealth", "VictimArmor", "ShooterWeapon", "VictimHealthDamage","VictimArmorDamage", "HitGroup",
	}
	if err := writer.Write(header); err != nil {
		return err // let's return errors if necessary, rather than having a one-size-fits-all error handler
	}

	// data
	for _, frameData := range data {
		for _, player := range frameData.Players {
			err := writer.Write(player)
			if err != nil {
				return err
			}
		}
	}

	return nil
}

// Error Checking and other Helpers
func checkError(err error) {
	if err != nil {
		panic(err)
	}
}