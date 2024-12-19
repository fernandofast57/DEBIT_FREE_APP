
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("NobleGoldSystem", function () {
    let nobleGoldSystem;
    let owner;
    let user1;
    let user2;
    let user3;

    beforeEach(async function () {
        [owner, user1, user2, user3] = await ethers.getSigners();
        
        const NobleGoldSystem = await ethers.getContractFactory("NobleGoldSystem");
        nobleGoldSystem = await NobleGoldSystem.deploy();
        await nobleGoldSystem.waitForDeployment();
    });

    describe("Transformations", function () {
        it("Should process batch transformations correctly", async function () {
            const users = [user1.address, user2.address];
            const euroAmounts = [ethers.parseEther("1000"), ethers.parseEther("2000")];
            const goldGrams = [ethers.parseEther("10"), ethers.parseEther("20")];

            await expect(nobleGoldSystem.batchTransform(users, euroAmounts, goldGrams))
                .to.emit(nobleGoldSystem, "GoldTransformed")
                .withArgs(user1.address, euroAmounts[0], goldGrams[0], await time.latest());

            const user1Investments = await nobleGoldSystem.getInvestments(user1.address);
            expect(user1Investments.length).to.equal(1);
            expect(user1Investments[0].euroAmount).to.equal(euroAmounts[0]);
        });
    });

    describe("Noble Ranks", function () {
        it("Should update ranks based on volume and referrals", async function () {
            await nobleGoldSystem.registerReferral(user2.address, user1.address);
            await nobleGoldSystem.registerReferral(user3.address, user1.address);

            const largeAmount = ethers.parseEther("50000");
            const goldGrams = ethers.parseEther("500");

            await nobleGoldSystem.batchTransform(
                [user2.address], 
                [largeAmount],
                [goldGrams]
            );

            const nobleInfo = await nobleGoldSystem.getNobleInfo(user1.address);
            expect(nobleInfo.rank).to.equal("viscount");
        });
    });

    describe("Bonus Distribution", function () {
        it("Should distribute bonuses correctly based on rank", async function () {
            await nobleGoldSystem.registerReferral(user2.address, user1.address);
            
            const hugeAmount = ethers.parseEther("100000");
            const goldGrams = ethers.parseEther("1000");
            
            await nobleGoldSystem.batchTransform(
                [user2.address, user2.address, user2.address, user2.address, 
                 user2.address, user2.address, user2.address, user2.address,
                 user2.address, user2.address],
                Array(10).fill(hugeAmount),
                Array(10).fill(goldGrams)
            );

            const investment = ethers.parseEther("1000");
            await expect(nobleGoldSystem.batchTransform(
                [user2.address],
                [investment],
                [ethers.parseEther("10")]
            )).to.emit(nobleGoldSystem, "BonusDistributed");

            const nobleInfo = await nobleGoldSystem.getNobleInfo(user1.address);
            expect(nobleInfo.rank).to.equal("count");
        });
    });

    describe("Referral System", function () {
        it("Should track referrals correctly", async function () {
            await nobleGoldSystem.registerReferral(user2.address, user1.address);
            await nobleGoldSystem.registerReferral(user3.address, user1.address);

            const referrals = await nobleGoldSystem.getReferrals(user1.address);
            expect(referrals.length).to.equal(2);
            expect(referrals[0]).to.equal(user2.address);
            expect(referrals[1]).to.equal(user3.address);
        });
    });
});
